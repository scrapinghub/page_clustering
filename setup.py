from setuptools import setup


setup(
    name = 'page_clustering',
    version = '0.0.1',
    packages = ['page_clustering'],
    install_requires = [
        'numpy',
        'scikit-learn',
        'scrapely',
    ],
    keywords         = ['crawler', 'scrapy', 'scrapely', 'web'],
    classifiers      = [
        #'Framework :: Crawl Frontier',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
