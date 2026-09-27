# %%python - data.csv rocketrat_measurements.csv
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import re
from io import StringIO
import elpigraph
import sys
import os

orientation = (45, 45, 0) # (azim, elev, roll)
colors = ['red', 'green', 'blue', 'yellow'] # maps colors to datasets (ordered) 
numofNodes = 10

## Flags
# [boolean, default=False] plotRaw: If True, plot one column of data as a 2D graph. as3D will be False
# [boolean, default=False] as3D: If True, plot 3 principal components in a 3D graph space (instead of 2D)

# [int, default=10] nodeCount: The number of metro map nodes to plot. A higher node count generally includes more outliers.

# These are optional, and all are set to defaults if not specified.

def checkHeader(line): # search for proper column header
    pattern = r'\w*\s?,\s?\w*(,|\n)'
    result = re.match(pattern, line)
    if result: 
        return True
    else:
        return False
    
def checkColCount(line):
    colCount = len(line.split(','))
    return colCount

def main():
    argv = sys.argv
    colCountList = []
    if len(argv) <= 1:
        try: 
            argv = ''
            with open('args.txt', 'r') as temp:
                argv += temp.read()
            argv = argv.split(' ')
        except FileNotFoundError:
            if len(argv) <= 1:
                print("error: To execute without passing filenames as command-line arguments, provide at least 1 filename in a file called 'args.txt' in the same directory as this script.")
                return None
    as3D = False 
    plotRaw = False
    if "--plotraw" in map(str.lower, argv):
        plotRaw = True
    if "--as3d" in map(str.lower, argv):
        as3D = True
    as3D *= (not plotRaw)
                
    ingest = ''
    if len(argv) <= 1:
        print(f"error: You must pass at least 1 file as an argument in the args.txt file or as a command-line argument\nUsage: {sys.argv[0]} [example.csv example2.csv ...] [--plotRaw | --as3d]")
        return None
    found = []
    for _, arg in enumerate(argv[1:]):
        if not (arg.startswith('--')):
            if not (os.path.exists(arg)):
                print(f"warn: No file {arg} was found and will not be consolidated")
                continue
            with open(arg, 'r') as csv:
                header = csv.readline()
                if not checkHeader(header):
                    print(f"warn: File {arg} does not contain a valid header line and will not be consolidated")
                    continue
                headerColCount = checkColCount(header)
                body = csv.read()
                valid = True
                for _, l in enumerate(body.splitlines()):
                    if checkColCount(l) != headerColCount:
                        print(f"warn: File {arg} has at least 1 column count mismatch with header (one found at line {_+2}) and will not be consolidated")
                        valid = False
                        break
                if not valid: 
                    continue
                colCountList.append(headerColCount)
                ingest += body + '\n'
                found.append(arg)
        else:
            argv.pop(_)
    if len(set(colCountList)) != 1 and len(colCountList) > 0:
        print(f"error: Column counts across given files do not match")
        for _ in range(0, len(colCountList)):
            print(f"    {found[_]}: {colCountList[_]} column(s)")
        return None
  
    # Check for first line containing headers
    # Use regular expression to find "string,string"
    # The strings should contain alphabetic characters
    
    if len(found) >= 1:
        print(f"{len(found)}/{len(argv[1:])} files found. {found} will be used")
    else: 
        print("info: No files found. Exiting program...")
        return None
    ingest = re.sub(r'(?<=\d),', ' ', ingest)
 
    config = np.dtype({
        'names': ('target_names', 'data'),
        'formats': ('object', 'object')
    })
    # format csv data to be two sets of numpy arrays that hold objects, as defined by dtype config
    pre = ''
    try:
        pre = np.loadtxt(StringIO(ingest), dtype=config, delimiter=',', unpack=True)
    except:
        print(f"error: One or more provided data files could not be parsed.\nUsage: {sys.argv[0]} [example.csv example2.csv ...] [--plotRaw | --as3d]")
        print(f"A data file should hold one per line, with values separated by commas. The identifier (or 'name') should numerical values.")
        print(f"'Name',val1,val2,val3...\n'Name',val1,val2,val3...\n'Name2',val1,val2,val3...")
        return None
    data = {}
    for i, _ in enumerate(config.names):
        data[_] = pre[i]
    data['data'] = data['data'].tolist()

    X = data['data']
    y = []
    target_names = list(dict.fromkeys(data['target_names']))

    # map each datum to an integer identifier instead of referencing each name 
    for _ in range(len(X)):
        X[_] = [float(i) for i in X[_].split(' ')]
        y.append(target_names.index(data['target_names'][_]))

    y = np.array(y)
    X = np.array(X)

    # standardize and reduce to 2D
    if plotRaw:
        X_pca = X[:, 3]
        X_pca = np.column_stack((np.arange(len(X_pca)), X_pca))
        
    else:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        pca = PCA(n_components=2+(1*as3D))
        X_pca = pca.fit_transform(X_scaled)
    
    if not plotRaw:
        # Fit principal tree - returns a LIST of trees
        n_nodes = numofNodes
        trees = elpigraph.computeElasticPrincipalTree(X_pca, NumNodes=n_nodes, Mu=0.1, Lambda=0.01)

        # Extract the FIRST tree from the list
        tree = trees[0]  # Get first tree from list
        nodes = tree['NodePositions']
        edges = tree['Edges'][0]

        from scipy.spatial import cKDTree
        node_tree = cKDTree(nodes)
        partition = node_tree.query(X_pca)[1]

    # Create figure
    if as3D: 
        fig = plt.figure(1, figsize=(8, 6))
        ax = fig.add_subplot(111, projection="3d", azim=orientation[0], elev=orientation[1], roll=orientation[2])
        ### Use AX instead of PLT for all 3D projection code
    else:
        plt.figure(figsize=(10, 8))

    # Plot data points colored by species
    for i, species in enumerate(target_names):
        mask = y == i
        if as3D:
            ax.scatter(X_pca[mask, 0], X_pca[mask, 1], X_pca[mask, 2],
                        color=colors[i], alpha=0.5, s=30, 
                        label=species)
        else:
            plt.scatter(X_pca[mask, 0], X_pca[mask, 1],
                    color=colors[i], alpha=0.5, s=30, 
                    label=species)
        
    if not plotRaw:
        # Draw tree edges
        for edge in edges:
            if as3D:
                ax.plot([nodes[edge[0], 0], nodes[edge[1], 0]],
                        [nodes[edge[0], 1], nodes[edge[1], 1]],
                        [nodes[edge[0], 2], nodes[edge[1], 2]],
                        'k-', linewidth=2, zorder=2)
            else:
                plt.plot([nodes[edge[0], 0], nodes[edge[1], 0]],
                         [nodes[edge[0], 1], nodes[edge[1], 1]],
                         'k-', linewidth=2, zorder=2)

        node_counts = np.zeros(len(nodes))
        for node_id in partition:
            node_counts[node_id] += 1
        # Scale node size by number of points
        node_sizes = 80 + (node_counts / np.max(node_counts) * 120)
        
        for i, node in enumerate(nodes):
                if as3D:
                    ax.scatter(node[0], node[1], node[2],
                        s=node_sizes[i], color='black', marker='o', 
                        edgecolors='white', linewidth=2, 
                        zorder=5, alpha=0.8)
                else:
                    plt.scatter(node[0], node[1],
                        s=node_sizes[i], color='black', marker='o', 
                        edgecolors='white', linewidth=2, 
                        zorder=5, alpha=0.8)
 

    # Add labels and legend
    if not plotRaw:
        if (as3D):
            ax.set(
                title=f'Principal tree ({n_nodes} nodes), 3D',
                xlabel="Principal component 1",
                ylabel="Principal component 2",
                zlabel="Principal component 3",
            )
            ax.xaxis.set_ticklabels([])
            ax.yaxis.set_ticklabels([])
            ax.zaxis.set_ticklabels([])
            ax.legend()
        else:
            plt.xlabel('Principal component 1')
            plt.ylabel('Principal component 2')
            plt.title(f'Principal tree ({n_nodes} nodes), 2D')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
    else:
        plt.xlabel('Index')
        plt.ylabel('Attribute')
        plt.title(f'Raw plot')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
    plt.show()
    
if __name__ == '__main__':
    main()

# %%
