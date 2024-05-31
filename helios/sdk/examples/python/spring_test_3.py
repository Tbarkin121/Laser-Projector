import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay

# Load data
# Make sure to convert 'donut200.mat' to a Python-friendly format like 'donut200.npy'
# and load using np.load. Assuming 'pts' and 't' are stored in 'donut200.npy'.
data = np.load('donut100.npy', allow_pickle=True).item()

pts = data['pts']
t = data['t']
N = len(pts)

cntr = np.array([0, 1])
v0 = np.array([0, 0])
dt = 0.001
omega = 0
k_sp = 1e5
b_sp = 50
C_s = 0.15

iter_max = 10000
y_floor = 0
g = -9.8
frame_skip = 1
axis_vec = [-3, 3, -3, 3]

# Build element list
pts += np.ones((N, 1)) * cntr
p2p = [None] * N
el = np.zeros((0, 2), dtype=int)

for i in range(N):
    idx, _ = np.where(t == i)
    p2p[i] = np.unique(t[np.sort(idx), :])
    p2p[i] = p2p[i][p2p[i] != i]
    
    for j in p2p[i]:
        el_curr = np.sort([i, j])
        if not np.any(np.all(el == el_curr, axis=1)) and i != j:
            el = np.vstack([el, el_curr])

# Build point to element mapping
Nel = len(el)
p2e = [None] * N
for i in range(N):
    idx, _ = np.where(el == i)
    p2e[i] = np.sort(idx)

r = pts[el[:, 0], :] - pts[el[:, 1], :]
L_rest = np.sqrt(np.sum(r**2, axis=1))
Fs = np.zeros((N, 2))
Fd = np.zeros((N, 2))

rotMat = np.array([[np.cos(omega*dt), -np.sin(omega*dt)],
                   [np.sin(omega*dt), np.cos(omega*dt)]])

X0 = pts
X1 = (pts - np.ones((N, 1)) * cntr) @ rotMat.T + np.ones((N, 1)) * cntr
X1 += dt * np.ones((N, 1)) * v0

plt.figure()
for j in range(iter_max):
    for i in range(N):
        r_i = X1[i, :] - X1[p2p[i], :]
        r_o = X0[i, :] - X0[p2p[i], :]
        r_hat_i = r_i / np.linalg.norm(r_i, axis=1)[:, np.newaxis]
        L_i = np.linalg.norm(r_i, axis=1)
        L_o = np.linalg.norm(r_o, axis=1)
        dL_i = L_rest[p2e[i]] - L_i
        dLdt_i = (L_o - L_i) / dt
        fs_i = k_sp * r_hat_i * (dL_i[:, np.newaxis])
        Fs[i, :] = np.sum(fs_i, axis=0)
        fd_i = b_sp * r_hat_i * (dLdt_i[:, np.newaxis])
        Fd[i, :] = np.sum(fd_i, axis=0)

    Fg = g * np.ones((N, 1)) * [0, 1]
    F = Fs + Fd + Fg
    X2 = dt**2 * F + 2 * X1 - X0
    
    idx = X2[:, 1] < y_floor
    X2[idx, 1] = y_floor
    X2[idx, 0] += C_s * dt * F[idx, 1] * (X2[idx, 0] - X1[idx, 0])

    X0 = X1
    X1 = X2

    if j % frame_skip == 0:
        plt.clf()
        plt.triplot(X2[:, 0], X2[:, 1], t)
        plt.axis(axis_vec)
        plt.axis('equal')
        plt.grid(True)
        plt.draw()
        plt.pause(0.01)

plt.show()
