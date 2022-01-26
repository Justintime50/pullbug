import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

REQUIREMENTS = [
    'PyGithub == 1.*',
    'requests == 2.*',
    'slackclient == 2.*',
    'typing_extensions',  # TODO: Remove once we drop support for Python 3.7
    'woodchips == 0.2.*',
]

DEV_REQUIREMENTS = [
    'black',
    'coveralls == 3.*',
    'flake8',
    'isort',
    'mypy',
    'pytest == 6.*',
    'pytest-cov == 2.*',
    'types-requests',
]

setuptools.setup(
    name='pullbug',
    version='3.2.1',
    description='Get bugged via Discord, Slack, or RocketChat to merge your GitHub pull requests.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/justintime50/pullbug',
    author='Justintime50',
    license='MIT',
    packages=setuptools.find_packages(),
    package_data={'pullbug': ['py.typed']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIREMENTS,
    extras_require={
        'dev': DEV_REQUIREMENTS,
    },
    entry_points={
        'console_scripts': [
            'pullbug=pullbug.cli:main',
        ],
    },
    python_requires='>=3.7, <4',
)
