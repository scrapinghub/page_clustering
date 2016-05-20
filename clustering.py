from sklearn.cluster import MiniBatchKMeans
import numpy as np

from features import TagFrequency


class OnlineKMeans(object):
    def __init__(self, n_clusters=8, batch_size=None,
                 max_std_dev=5.0, min_cluster_points=30, vectorizer=TagFrequency()):
        """
        Parameters
        ----------
        n_clusters : int
            Number of clusters to use for KMeans
        batch_size : int
            Update clusters only when the batch reaches this size
            Default: batch_size = 10*n_clusters
        max_std_dev : float
            For outlier detection, do not cluster measures that whose
            distance exceeds 5 times the std dev of the cluster
            Set to None to disable outlier detection
            This value can be updated at any point after object creation
        min_cluster_points : int
            Do not perform outlier detection on clusters that have less than
            this amount of points
        vectorizer : callable
            Takes an scrapely.htmlpage.HtmlPage and returns a numpy array.
            Different pages can return different array sizes. If the vector
            is missing values they are assumed to be zero.
        """
        self.vectorizer = vectorizer
        self.dimension = 0

        if batch_size is None:
            self.batch_size = 10*n_clusters
        else:
            self.batch_size = batch_size
        self.batch = []
        self.n_clusters = n_clusters
        self.kmeans = MiniBatchKMeans(self.n_clusters)

        # outlier_detection parameters
        self._sum_sqr_dist = np.zeros((self.n_clusters,))
        self.max_std_dev = max_std_dev
        self.min_cluster_points = min_cluster_points

    @property
    def outlier_detection(self):
        """True if outlier detection active"""
        return self.max_std_dev is not None

    @property
    def is_fit(self):
        """True if cluster centers available"""
        return hasattr(self.kmeans, 'cluster_centers_')

    @property
    def _cluster_variance(self):
        """An array with the cluster variance for each cluster"""
        return self._sum_sqr_dist/self.kmeans.counts_

    def _sqr_distance_to_center(self, X, y=None):
        """Compute the distance of X to cluster center y"""
        if y is None:
            y = self.kmeans.predict(X)
        return np.sum((X - self.kmeans.cluster_centers_[y])**2, axis=1)

    def _find_outliers(self, X, y=None):
        """Return a boolean array of size X.shape[0] where a True entry means
        that the point is an outlier"""
        if not self.is_fit:
            return np.zeros((X.shape[0],))
        if y is None:
            y = self.kmeans.predict(X)
        return np.logical_and(
            self.kmeans.counts_[y]>self.min_cluster_points,
            (self._sqr_distance_to_center(X, y)/
             self._cluster_variance[y]) > self.max_std_dev**2)

    def add_page(self, page):
        """Update cluster centers with new page"""
        x = self.vectorizer(page)
        self.batch.append(x)
        if len(self.batch) >= self.batch_size:
            # load batch data
            dimension_new = len(x)
            X_batch = np.zeros((self.batch_size, dimension_new))
            for i, x_batch in enumerate(self.batch):
                X_batch[i, :len(x_batch)] = x_batch
            self.batch = []
            # update dimension of cluster centers
            if dimension_new > self.dimension:
                if self.is_fit:
                    centers_new = np.zeros((self.n_clusters, dimension_new))
                    centers_new[:, :self.dimension] = self.kmeans.cluster_centers_
                    self.kmeans.cluster_centers_ = centers_new
                self.dimension = dimension_new
            # filter out outliers
            if self.outlier_detection:
                X_batch = X_batch[np.logical_not(self._find_outliers(X_batch))]
            # fit data
            self.kmeans.partial_fit(X_batch)
            # update cluster variance
            y_batch = self.kmeans.predict(X_batch)
            D_batch = self._sqr_distance_to_center(X_batch, y_batch)
            for (y, d) in zip(y_batch, D_batch):
                self._sum_sqr_dist[y] += d

    def classify(self, page):
        """Return cluster index or -1 if outlier and outlier detection is active"""
        X = self.vectorizer(page)[:self.dimension].reshape(1, -1)
        y = self.kmeans.predict(X)
        if self.outlier_detection and self._find_outliers(X, y)[0]:
            return -1
        return y[0]
