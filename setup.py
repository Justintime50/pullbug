import setuptools


with open('README.md', 'r') as fh:
    long_description = fh.read()

REQUIREMENTS = [
    'PyGithub == 1.*',
    'requests == 2.*',
    'slackclient == 2.*',
    'woodchips == 0.2.*',
]

DEV_REQUIREMENTS = [
    'bandit == 1.7.*',
    'black == 23.*',
    'build == 0.10.*',
    'flake8 == 6.*',
    'isort == 5.*',
    'mypy == 1.3.*',
    'pytest == 7.*',
    'pytest-cov == 4.*',
    'twine == 4.*',
    'types-requests',
]

setuptools.setup(
    name='pullbug',
    version='5.0.0',
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
    python_requires='>=3.8, <4',
)
