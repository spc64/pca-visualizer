pca-visualizer is based on the following:
* iris_metromap_2.py
* Python 3.12.11
* CentOS Stream 10
* Reads plain text files in .csv format

pca-visualizer is run from the command line in a terminal. The program requires a list of .csv files to read from that must be provided as either arguments or in a separate file named 'args.txt' in the same directory as the program. For example:

    $ python iris_metromap_2.py

has no arguments and will look for input files in an args.txt file. An args.txt file should be formatted as such:

    - file1.csv [file2.csv] ... [flags]

The same syntax can be used in the command line itself, although note that the '-' prefix must be removed.

    $ python iris_metromap_2.py file1.csv [file2.csv] ... [flags]

The program has three optional flags that can be put either in args.txt or on the command line:
* \[boolean] --plotRaw: If True, plot one column of data as a 2D graph. as3D will be False
* \[boolean] --as3D: If True, plot 3 principal components in a 3D graph space (instead of 2D)
* \[int] --nodeCount: The number of metro map nodes to plot. A higher node count generally includes more outliers.

If not specified, the program will assume the --plotRaw and --as3D flags to be False and --nodeCount to be 10. This will perform PCA on the consolidated data set with two principal components. In this instance, the program will output a two-dimensional plot of a node tree with 10 nodes, with individual sample points represented as colored dots along the tree.

Two non-compatible example data sets are provided alongside the program (data.csv, data2.csv). They are to showcase functionality and do not represent realistic values nor sample distributions for what they nominally describe.