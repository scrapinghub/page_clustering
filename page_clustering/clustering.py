import scrapely.htmlpage as hp
from sklearn.cluster import MiniBatchKMeans
import numpy as np

from features import TagFrequency


def reshape_cols(X, n):
    """Append with zero columns X until it has n columns"""
    Y = np.zeros((X.shape[0], n))
    Y[:, :X.shape[1]] = X
    return Y


class OnlineKMeans(object):
    def __init__(self, n_clusters=8, batch_size=None,
                 max_std_dev=5.0, min_cluster_points=30,
                 vectorizer=TagFrequency(), centers=None):
        """
        Parameters
        ----------
        n_clusters : int
            Number of clusters to use for KMeans.
        batch_size : int
            Update clusters only when the batch reaches this size.
            Default: batch_size = 10*n_clusters.
        max_std_dev : float
            For outlier detection, do not cluster measures whose
            distance exceeds 5 times the std dev of the cluster.
            Set to None to disable outlier detection.
            This value can be updated at any point after object creation.
        min_cluster_points : int
            Do not perform outlier detection on clusters that have less than
            this amount of points.
        vectorizer : callable
            Takes an scrapely.htmlpage.HtmlPage and returns a numpy array.
            Different pages can return different array sizes. If the vector
            is missing values they are assumed to be zero.
        """
        self.vectorizer = vectorizer
        self.dimension = vectorizer.dimension

        if batch_size is None:
            self.batch_size = 10*n_clusters
        else:
            self.batch_size = batch_size
        self.batch = []
        self.n_clusters = n_clusters if centers is None else centers.shape[0]
        self.kmeans = MiniBatchKMeans(
            self.n_clusters,
            init=centers if centers is not None else 'k-means++')

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
                    self.kmeans.cluster_centers_ = reshape_cols(
                        self.kmeans.cluster_centers_, dimension_new)
                elif isinstance(self.kmeans.init, np.ndarray):
                    self.kmeans.init = reshape_cols(
                        self.kmeans.init, dimension_new)
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
        """Return cluster index or -1 if outlier and outlier detection is active.

        page : scrapely.htmlpage.HtmlPage
        """
        X = self.vectorizer(page)[:self.dimension].reshape(1, -1)
        y = self.kmeans.predict(X)
        if self.outlier_detection and self._find_outliers(X, y)[0]:
            return -1
        return y[0]


def kmeans_from_samples(samples):
    """Initializes and returns the clustering using the provided samples.

    samples : Iterable[sample]
        A sample can be either:
            - a dict with `url` and `original_body` keys.
            - an string with the page body

    Returns : OnlineKMeans
    """
    def build_htmlpage(sample):
        if isinstance(sample, (str, unicode)):
            url = ''
            body = sample
        else:
            url = sample.get('url')
            body = sample.get('original_body', sample.get('annotated_body'))
        return hp.HtmlPage(url=url, body=body)
    pages = map(build_htmlpage, samples)
    n_clusters = len(pages)
    vectorizer = TagFrequency()
    centers = map(vectorizer, pages)
    X = np.zeros((len(centers), vectorizer.dimension))
    for i, c in enumerate(centers):
        X[i, :len(c)] = c
    return OnlineKMeans(
        n_clusters=n_clusters,
        centers=X,
        vectorizer=vectorizer)
