import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay

def dist_mesh_donut(N, iter_max, k_s, r_i, r_o, L_rest, plot_stat, frame_skip):
    X = np.ones((N, 1)) * np.array([0.5, 0.5]) - np.random.rand(N, 2)
    Fs = np.zeros((N, 2))

    if plot_stat.lower() == 'on':
        plt.figure()

    for k in range(iter_max):
        t = Delaunay(X).simplices
        
        cntrds = (X[t[:, 0], :] + X[t[:, 1], :] + X[t[:, 2], :]) / 3
        cntrds_r = np.sqrt(np.sum(cntrds**2, axis=1))
        idx_0 = cntrds_r < r_i
        t = t[~idx_0, :]
        
        for i in range(N):
            idx_1, _ = np.where(t == i)
            p2p = np.unique(t[np.sort(idx_1), :])
            p2p = p2p[p2p != i]
            
            r = X[i, :] - X[p2p, :]
            r_hat = r / (np.sqrt(np.sum(r**2, axis=1))[:, np.newaxis])
            dL_i = L_rest - np.sqrt(np.sum(r**2, axis=1))
            Fs[i, :] = np.sum(r_hat * (dL_i[:, np.newaxis]), axis=0)
        
        X = k_s * Fs + X
        
        Xr = np.sqrt(np.sum(X**2, axis=1))
        idx_2 = Xr > r_o
        idx_3 = Xr < r_i
        X[idx_2, :] = r_o * X[idx_2, :] / (Xr[idx_2, np.newaxis])
        X[idx_3, :] = r_i * X[idx_3, :] / (Xr[idx_3, np.newaxis])

        if k % frame_skip == 0 and plot_stat.lower() == 'on':
            plt.triplot(X[:, 0], X[:, 1], t)
            plt.title(f'{k}')
            plt.axis('equal')
            plt.axis(r_o * np.array([-1, 1, -1, 1]))
            plt.draw()
            plt.pause(0.001)
            plt.clf()  # Clear the figure to ready the plot for next iteration

    plt.show()
    
    return t, X

#%%

#%%
N = 100;
k_s = .35;
L_rest = 0.15;
r_i = .5;
r_o = 1;
iter_max = 1000;
plot_stat ='on'
frame_skip = 1;

[t,pts] = dist_mesh_donut(N,iter_max,k_s,r_i,r_o,L_rest,plot_stat,frame_skip)

# Save the data
np.save(f'donut{N}.npy', {'t': t, 'pts': pts})  # Saves as a dictionary in a single file