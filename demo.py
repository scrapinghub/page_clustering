import sys
import os
import time

import scrapely.htmlpage as hp

import clustering


if __name__ == '__main__':
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = 'news.ycombinator.com'
    for dirpath, dnames, fnames in os.walk(path):
        pages = []
        for fname in fnames:
            full_path = os.path.abspath(os.path.join(dirpath, fname))
            with open(full_path, 'r') as inp:
                try:
                    body = inp.read().decode('utf-8')
                except UnicodeDecodeError:
                    continue
                pages.append(
                    hp.HtmlPage(url='file://' + full_path, body=body))
        print 'Total pages: {0}'.format(len(pages))

        t1 = time.clock()
        kmeans = clustering.OnlineKMeans()
        for page in pages:
            kmeans.add_page(page)
        t2 = time.clock()
        print 'Clustering in {0} seconds'.format(t2 - t1)
        print '    per page: {0} ms'.format((t2 - t1)/len(pages)*1000)

        for page in pages:
            print page.url, kmeans.classify(page)
