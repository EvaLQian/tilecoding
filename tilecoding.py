#!/usr/bin/env python
from __future__ import print_function
import numpy as np

class tilecoder:
  def __init__(self, dims, limits, tilings, offset=lambda n: 2 * np.arange(n) + 1):
    offset_vec = offset(len(dims))
    tiling_dims = np.array(dims, dtype=np.int) + offset_vec
    self._offsets = offset_vec * np.repeat([np.arange(tilings)], len(dims), 0).T / float(tilings)
    self._limits = np.array(limits)
    self._norm_dims = np.array(dims) / (self._limits[:, 1] - self._limits[:, 0])
    self._tile_base_ind = np.prod(tiling_dims) * np.arange(tilings)
    self._hash_vec = np.ones(len(dims), dtype=np.int)
    for i in range(len(dims) - 1):
      self._hash_vec[i + 1] = tiling_dims[i] * self._hash_vec[i]
    self._n_tiles = tilings * np.prod(tiling_dims)

  @property
  def n_tiles(self):
    return self._n_tiles
  
  def __getitem__(self, x):
    off_coords = ((x - self._limits[:, 0]) * self._norm_dims + self._offsets).astype(int)
    return self._tile_base_ind + np.dot(off_coords, self._hash_vec)

def example():
  import matplotlib.pyplot as plt
  from mpl_toolkits.mplot3d import Axes3D
  import time

  # tile coder dimensions, limits, tilings, step size, and offset vector
  dims = [8, 8]
  lims = [(0, 2.0 * np.pi)] * 2
  tilings = 8

  # create tile coder
  T = tilecoder(dims, lims, tilings)

  # learning params
  theta = np.zeros(T.n_tiles)
  alpha = 0.1 / tilings

  # target function with gaussian noise
  def target_ftn(x, y, noise=True):
    return np.sin(x) + np.cos(y) + noise * np.random.randn() * 0.1

  # randomly sample target function until convergence
  timer = time.time()
  batch_size = 100
  for iters in range(100):
    mse = 0.0
    for b in range(batch_size):
      xi = lims[0][0] + np.random.random() * (lims[0][1] - lims[0][0])
      yi = lims[1][0] + np.random.random() * (lims[1][1] - lims[1][0])
      zi = target_ftn(xi, yi)
      theta[T[xi, yi]] += alpha * (zi - theta[T[xi, yi]].sum())
      mse += (theta[T[xi, yi]].sum() - zi) ** 2
    mse /= batch_size
    print('samples:', (iters + 1) * batch_size, 'batch_mse:', mse)
  print('elapsed time:', time.time() - timer)

  # get learned function
  print('mapping function...')
  res = 200
  x = np.arange(lims[0][0], lims[0][1], (lims[0][1] - lims[0][0]) / res)
  y = np.arange(lims[1][0], lims[1][1], (lims[1][1] - lims[1][0]) / res)
  z = np.zeros([len(x), len(y)])
  for i in range(len(x)):
    for j in range(len(y)):
      z[i, j] = theta[T[x[i], y[j]]].sum()

  # plot
  fig = plt.figure()
  ax = fig.gca(projection='3d')
  X, Y = np.meshgrid(x, y)
  surf = ax.plot_surface(X, Y, z, cmap=plt.get_cmap('hot'))
  plt.show()

if __name__ == '__main__':
  example()
