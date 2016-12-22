from setuptools import setup, find_packages

import imp

version = imp.load_source('pybackend.version', 'pybackend/version.py')

setup(
    name='pybackend',
    version=version.version,
    description='Content annotation system machinery.',
    author='open-mic-dev',
    author_email='open-mic-dev@googlegroups.com',
    url='http://github.com/cosmir/open-mic',
    download_url='http://github.com/cosmir/open-mic/releases',
    packages=find_packages(),
    package_data={},
    long_description="""Content annotation system machinery.""",
    classifiers=[
        "License :: OSI Approved :: MIT License (MIT)",
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    keywords='audio music sound',
    license='MIT',
    install_requires=[
        'audioread >= 2.0.0',
        'Flask >= 0.11.1',
        'Flask-Cors >= 3.0.2',
        'requests',
        'google-cloud >= 0.22.0',
        'six >= 1.3'
    ],
    extras_require={
        'tests': ['pytest', 'pytest-cov']
    }
)
