# Description [![Build Status](https://travis-ci.org/scrapinghub/page_clustering.svg?branch=master)](https://travis-ci.org/scrapinghub/page_clustering)
A simple algorithm for clustering web pages.
A wrapper around [KMeans](http://scikit-learn.org/stable/modules/generated/sklearn.cluster.MiniBatchKMeans.html#sklearn.cluster.MiniBatchKMeans).
Web pages are converted to vectors, where each vector entry is just the count of a given tag and class attribute.
The dimension of the vectors will change as new pages with new tags or class attributes arrive.
Also a simple outlier detection is available and enabled by default. This allows for rejecting web pages
that are highly improbable to belong to any cluster.

# Install
    pip install page_clustering

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
    wget -r --quota=5M https://news.ycombinator.com
    python demo.py news.ycombinator.com

# Tests
    cd tests
    py.test

# Algorithm

The first part, vectorization, transforms the web page to a vector. For example,
take the following page:

```html
<html>
<body>
<ul class="list1">
    <li>A</li>
	<li>B</li>
</ul>
<ul class="list2">
    <li>Y</li>
	<li>Z</li>
</ul>
</body>
</html>
```

Each non-closing (tag, class) pair is mapped to a vector position and the number
of times it appears in the document is the value of the vector at that position.

| tag, class | position | count |
|------------|----------|-------|
| html       | 0        | 1     |
| body       | 1        | 1     |
| ul, list1  | 2        | 1     |
| li         | 3        | 4     |
| ul, list2  | 4        | 1     |

The vector is therefore `[1, 1, 1, 4, 1]`

When a new page arrives it can be possible that new (tag, class) pairs appear.
For example imagine that this new page arrives:

```html
<html>
<body>
<p>Another page with a paragraph tag </p>
</body>
</html>
```

The new page would be mapped according to this table:

| tag, class | position | count |
|------------|----------|-------|
| html       | 0        | 1     |
| body       | 1        | 1     |
| ul, list1  | 2        | 0     |
| li         | 3        | 0     |
| ul, list2  | 4        | 0     |
| p          | 5        | 1     |

The vector for this page would be `[1, 1, 0, 0, 0, 1]`.
The new vector has 6 dimensions, this means that the previous page vector needs
to be extended accordingly with zeros to the right: `[1, 1, 1, 4, 1, 0]`.

Once all needed pages are vectorized, KMeans is applied.
