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
    tests_requires = [
        'pytest'
    ]
)
