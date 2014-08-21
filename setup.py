from distutils.core import setup

setup(
    name='PGeo',
    version='0.1.1',
    author='Simone Murzilli; Guido Barbaglia',
    author_email='geobrickspy@gmail.com',
    packages=['pgeo'],
    url='http://pypi.python.org/pypi/PGeo/',
    license='LICENSE.txt',
    description='PGeo module.',
    long_description=open('README.md').read(),
    install_requires=[
        'pymongo >= 2.7.1',
        'psycopg2 >= 2.4.5',
        'GDAL >= 1.10.1',
        'httplib2 >= 0.8'
    ]
)
