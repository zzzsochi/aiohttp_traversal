from setuptools import setup


setup(
    name='aiohttp_traversal',
    version='0.10.0',
    description='Traversal based router for aiohttp.web',
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP",
    ],
    author='Alexander Zelenyak',
    author_email='zzz.sochi@gmail.com',
    license='BSD',
    url='https://github.com/zzzsochi/aiohttp_traversal',
    keywords=['asyncio', 'aiohttp', 'traversal', 'pyramid'],
    packages=['aiohttp_traversal', 'aiohttp_traversal.ext'],
    install_requires=[
        'aiohttp >=2.0',
        'resolver_deco',
        'zope.dottedname',
    ],
    tests_require=['pytest']
),
