# Description
A simple algorithm for clustering web pages.
A wrapper around [KMeans](http://scikit-learn.org/stable/modules/generated/sklearn.cluster.MiniBatchKMeans.html#sklearn.cluster.MiniBatchKMeans).
Web pages are converted to vectors, where each vector entry is just the count of a given tag and class attribute.
The dimension of the vectors will change as new pages with new tags or class attributes arrive.
Also a simple outlier detection is available and enabled by default. This allows for rejecting web pages
that are highly improbable to belong to any cluster.

# Usage
    import page_clustering

    clt = page_clustering.OnlineKMeans(n_clusters=5)
    # `pages` must have been obtained somehow
	for page in pages:
	    clt.add_page(page)
	y = clt.classify(new_page)
	for page in more_pages:
	    clt.add_page(page)
	y = clt.classify(yet_another_page)

# Demo
    wget -r --quota=15M https://news.ycombinator.com
    python demo.py news.ycombinator.com
