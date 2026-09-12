# %%
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import mpl_toolkits.mplot3d 

config = np.dtype({
    'names': ('target_names', 'data'),
    'formats': ('object', 'object')
})
pre = np.loadtxt('rocketrat_measurements.csv', dtype=config, delimiter=',', unpack=True)
data = {}
for i, _ in enumerate(config.names):
    data[_] = pre[i]
data['data'] = data['data'].tolist()


X = data['data']

for _ in range(len(X)):
    X[_] = [float(i) for i in X[_].split(' ')]

y = np.array(y)
X = np.array(X)

x = X[:, 0]
y = np.arange(1, len(x) + 1)

print(len(x))

plt.figure(figsize=(10, 8))
plt.bar(y, x)                # Create the plot
plt.xlabel('X axis')          # Label for X axis
plt.ylabel('Y axis')          # Label for Y axis
plt.title('X-Y Plot')         # Title of the plot
plt.show()                    # Display the plot


# %%
