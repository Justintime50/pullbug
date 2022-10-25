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
    'bandit == 1.7.*',
    'black == 22.*',
    'build == 0.7.*',
    'coveralls == 3.*',
    'flake8 == 4.*',
    'isort == 5.*',
    'mypy == 0.942',
    'pytest == 7.*',
    'pytest-cov == 3.*',
    'twine == 4.*',
    'types-requests',
]

setuptools.setup(
    name='pullbug',
    version='4.5.0',
    description='Get bugged via Discord or Slack to merge your GitHub pull requests or close open issues.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/justintime50/pullbug',
    author='Justintime50',
    license='MIT',
    packages=setuptools.find_packages(
        exclude=[
            'examples',
            'test',
        ]
    ),
    package_data={
        'pullbug': [
            'py.typed',
        ]
    },
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
