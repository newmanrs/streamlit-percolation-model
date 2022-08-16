import numpy as np
import pandas as pd
import altair as alt
from numpy.random import Generator, PCG64
from collections import defaultdict


class PercolationSimulation():

    def __init__(self, Nx = 10, Ny = 10, p=0.593):

        self.Nx = Nx
        self.Ny = Ny
        self.Nsites =  Nx*Ny
        self.rng = Generator(PCG64())
        self.precompute_neighbor_sites()
        self.reinitialize(Nx, Ny, p)

    def reinitialize(self, Nx, Ny, p):

        self.p = p
        if self.Nx != Nx or self.Ny != Ny:
            self.Nx = Nx
            self.Ny = Ny
            self.Nsites = Nx*Ny
            self.precompute_neighbor_sites()
        self.trial()

    def trial(self):
        """
        Generate random system and cluster sites
        """
        self.compute_sites()
        self.compute_clusters()
        return self

    def compute_sites(self):
        """
        Fill sites
        """
        self.sites = self.rng.random((self.Nx, self.Ny)) < self.p
        self.sites.astype(np.int32)

    def precompute_neighbor_sites(self):
        """
        Precompute sites of neighbors for the clustering loop
        """
        Nx = self.Nx
        Ny = self.Ny


        # neighbor_sites is dict of int -> (np.array(5,), np.array(5,))
        # outperforms numpy.zeros(shape = (Nx*Ny,2,5),dtype=np.int32)
        self.neighbor_sites = dict()
        idx_1d = -1

        for i in range(Nx):
            for j in range(Ny):
                idx_1d += 1
                neighs = [
                    ((i-1) % Nx, j),  # Left
                    (i, j),           # Center
                    ((i+1) % Nx, j),  # Right
                    (i, (j-1) % Ny),  # Down
                    (i, (j+1) % Ny),  # Up
                    ]
                # Allows for a numpy slice if we transpose
                # into a Nx2 set of tuples.  Hideously unreadable,
                # like most linear algebra code
                neighs = tuple(np.array(neighs,dtype=np.uint32).T)
                self.neighbor_sites[idx_1d] = neighs


    def compute_clusters(self):

        Nx = self.Nx
        Ny = self.Ny
        Nsites = Nx * Ny
        # Empty sites set to Nx*Ny+1 (larger than any possible id)
        # Initialize sites with sequentially increasing cluster id
        empty_id = Nx*Ny+1
        clusters = np.ones((Nx, Ny), dtype=np.uint32) * empty_id
        c = 1
        for i in range(Nx):
            for j in range(Ny):
                if self.sites[i, j]:
                    clusters[i, j] = c
                    c += 1


        # Brute force clustering loop.
        # Merge to minimum of cluster of ids neighboring iteratively
        # Runtime is probably O(Nx*Ny*max_cluster_path_length).
        # max cluster length in worst case (near percolation
        # threshold) can be significantly larger than max(Nx,Ny).
        any_change = True

        # Track number of iterations of bad algorithm
        self.cluster_iterations = 0

        while any_change:

            any_change = False
            self.cluster_iterations += 1
            idx_1d = -1 # 1D index into neighbor list

            for i in range(Nx):
                for j in range(Ny):
                    idx_1d += 1
                    if clusters[i, j] == empty_id:
                        continue

                    min_cl_id = min(clusters[self.neighbor_sites[idx_1d]])
                    # Compute min over self site and 4 neighbors
                    if clusters[i, j] != min_cl_id:
                        any_change = True
                        clusters[i, j] = min_cl_id

        clusters[clusters == empty_id] = 0  # Set noncluster id to 0

        # Cluster sizes
        cluster_sizes = defaultdict(int)
        for i in range(Nx):
            for j in range(Ny):
                if clusters[i, j] != 0:
                    cluster_sizes[clusters[i, j]] += 1
        # Sort clusters largest to smallest
        sorted_cluster_sizes = sorted(
            cluster_sizes.items(),
            key=lambda x: x[1],
            reverse=True)

        # Store in class
        self.clusters = clusters
        self.cluster_sizes = cluster_sizes
        self.sorted_cluster_sizes = sorted_cluster_sizes
        self.max_cluster_size = sorted_cluster_sizes[0][1]

    def get_chart(self,
            logarithmic_cluster_size = False):
        """
        Get heatmap
        """

        # Heatmap needs to color  by cluster size.
        self.heat_cluster_frac = np.zeros((self.Nx, self.Ny),dtype=np.float32)
        #self.heat_cluster_frac[:]= np.nan
        self.heat_cluster_size = np.zeros((self.Nx, self.Ny),dtype=np.int)
        self.heat_cluster_id = np.zeros((self.Nx, self.Ny),dtype=np.int)
        for cl_id, cl_size in self.sorted_cluster_sizes:
            if logarithmic_cluster_size == True:
                self.heat_cluster_frac[self.clusters == [cl_id]] = np.log(cl_size)
            else:
                frac = cl_size / self.Nsites
                self.heat_cluster_frac[self.clusters == [cl_id]] = frac
                self.heat_cluster_size[self.clusters == [cl_id]] = cl_size
                self.heat_cluster_id[self.clusters == [cl_id]] = cl_id


        i, j = np.meshgrid(range(0, self.Nx), range(0, self.Ny))
        df = pd.DataFrame(
            {
                'i': i.ravel(),
                'j': j.ravel(),
                'cluster site fraction': self.heat_cluster_frac.ravel(),
                'cluster size': self.heat_cluster_size.ravel(),
                'cluster id': self.heat_cluster_id.ravel(),
            }
            )

        chart_rect_width = 500 // np.max([self.Nx, self.Ny])
        if chart_rect_width == 0:
            chart_rect_width = 1 # min width 1 px


        chart_title = f"Site lattice percolation Nx = {self.Nx}, " \
            f"Ny = {self.Ny}"

        # mark_rect <--> heatmap
        chart = alt.Chart(df).mark_rect().encode(
            x='i:O',
            y='j:O',
            color=alt.Color('cluster site fraction:Q',
                scale=alt.Scale(
                    range=['purple','yellow', 'white','white'],
                    domain=[1.0, 0.999/(self.Nx*self.Ny), 0.999/(self.Nx * self.Ny),0.0]
                    )
                ),
            tooltip=['i', 'j', 'cluster site fraction', 'cluster size', 'cluster id']
        ).properties(
            height={'step': chart_rect_width},
            width={'step': chart_rect_width},
            title=chart_title
        ).configure_scale(
            # Gap between rectangles
            bandPaddingInner=0.1
        ).configure_title(
            fontSize=16,
            anchor='start'
        )

        return chart





        raise NotImplementedError("return df")
        # return dataframe
