# Tile Coding

[Tile coding](http://incompleteideas.net/book/ebook/node88.html#SECTION04232000000000000000) is a coarse coding function approximation method that uses several overlapping offset grids (tilings) to approximate a continuous space.

# Dependencies

* numpy

# Usage

A tile coder is instantiated with the following arguments:

* A list of the number of tiles spanning each dimension
* A list of tuples containing the value limits of each dimension
* The number of tilings
* (Optional) A function computing the offset amount for each dimension

Once instantiated, it uses ```__getitem__()``` to take a coordinate of a continuous space and return a numpy array with the indices of the active tiles. That is, it implicitly produces a binary vector of active tiles by returning the locations of the vector which have a ```1```.

## A Simple Example

Suppose we want to tile a continuous 2-dimensional space where the values of dimension range from ```0``` to ```10```. For this example, we'll have a tiling consist of ```10``` tiles spanning the range of values for each dimension (A ```10×10``` tiling), and use ```8``` offset tilings.

First, we import the tile coder:

```python
from tilecoding import TileCoder
```

Next, we specify the number of tiles spanning each dimension (tiling dimensions), the value limits of each dimension, and the number of tilings:

```python
# number of tile spanning each dimension
dims = [10, 10]
# value limits of each dimension
lims = [(0.0, 10.0), (0.0, 10.0)]
# number of tilings
tilings = 8
```

We can now instantiate a tile coder (which we'll denote ```T```):

```python
T = TileCoder(dims, lims, tilings)
```

The tile coder can then return the active tiles for given ```(x, y)``` coordinates in this 2-dimensional space via ```T[x, y]```:

```bash
# get active tiles for location (3.6, 7.21)
>>> T[3.6, 7.21]
array([ 80, 201, 322, 443, 565, 697, 807, 928])

# a nearby point, differs from (3.6, 7.21) by 1 tile
>>> T[3.7, 7.21]
array([ 80, 201, 322, 444, 565, 697, 807, 928])

# a slightly farther point, differs from (3.6, 7.21) by 5 tiles
>>> T[4.1, 7.10]
array([ 81, 202, 323, 444, 565, 686, 807, 928])

# a much farther point, no tiles in common with (3.6, 7.21)
>>> T[6.6, 9.14]
array([105, 226, 347, 468, 590, 722, 832, 953])
```

## Function Approximation Example

Suppose we want to approximate a continuous 2-dimensional function with a function that's linear in the tile coded binary representation. Let's approximate ```f(x, y) = sin(x) + cos(y)``` where the values of both ```x``` and ```y``` range from ```0``` to ```2π```, and we only have access to *noisy*, *online* samples of the function (within the specified range).

We'll use a tile coder with ```8``` tilings, each consisting of ```8``` tiles spanning the range of values in each direction (An ```8×8``` tiling):

```python
import numpy as np
from tilecoding import TileCoder

# tile coder dimensions, limits, tilings
dims = [8, 8]
lims = [(0.0, 2.0 * np.pi), (0.0, 2.0 * np.pi)]
tilings = 8

# create tile coder
T = TileCoder(dims, lims, tilings)
```

The following function will produce a noisy sample from our target function:

```python
# target function with gaussian noise
def target_fn(x, y):
  noise = 0.1 * np.random.randn()
  return np.sin(x) + np.cos(y) + noise
```

Our approximate (linear) function can be represented with a set of weights, one for each tile in the tile coder's tilings. We can get the total number of tiles in the tile coder's tilings using ```T.n_tiles```:

```python
# linear function weight vector
w = np.zeros(T.n_tiles)
```

We'll then take 10,000 online samples (i.e. we don't store them and only work with the most recent sample) at random locations of the target function. We can update our weights using stochastic gradient descent (SGD) in the mean squared error between the sample and our linear function's current estimate:

```python
# step size for SGD
alpha = 0.1 / tilings

# learn from 10,000 samples
for i in range(10000):
  # get a random location within the value limits
  x, y = 2.0 * np.pi * np.random.rand(2)
  # get a noisy sample from our target function at that location
  target = target_fn(x, y)
  # get the active tiles at that location
  tiles = T[x, y]
  # get our current prediction at that location
  pred = w[tiles].sum()
  # update weights with SGD
  w[tiles] += alpha * (target - pred)
```

We can check how good our learned approximation is by evaluating our approximate function against the true target function at various points:

```bash
# check approximate value at (2.5, 3.1)
>>> tiles = T[2.5, 3.1]
>>> w[tiles].sum()
-0.40287006579746704
# compare to true value at (0.5, 1.2)
>>> np.sin(2.5) + np.cos(3.1)
-0.40066300616932304
```

Alternatively, we can plot a surface of our learned approximation (i.e. with matplotlib):

```python
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# resolution
res = 200

# (x, y) space to evaluate
x = np.arange(0.0, 2.0 * np.pi, 2.0 * np.pi / res)
y = np.arange(0.0, 2.0 * np.pi, 2.0 * np.pi / res)

# map the function across the above space
z = np.zeros([len(x), len(y)])
for i in range(len(x)):
  for j in range(len(y)):
    tiles = T[x[i], y[j]]
    z[i, j] = w[tiles].sum()

# plot function
fig = plt.figure()
ax = fig.gca(projection='3d')
X, Y = np.meshgrid(x, y)
surf = ax.plot_surface(X, Y, z, cmap=plt.get_cmap('hot'))
plt.show()
```

<p align="center">
  <img src="images/tc_sincos.png" width=480>
</p>
