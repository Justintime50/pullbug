import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

REQUIREMENTS = [
    'requests == 2.*',
    'slackclient == 2.*',
    'python-dotenv == 0.19.*',  # TODO: Remove once we convert env variables to CLI args
]

DEV_REQUIREMENTS = [
    'coveralls == 3.*',
    'flake8',
    'pytest == 6.*',
    'pytest-cov == 2.*',
]

setuptools.setup(
    name='pullbug',
    version='2.4.0',
    description=(
        'Get bugged via Discord, Slack, or RocketChat to merge your GitHub pull requests or GitLab merge requests.'
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/justintime50/pull-bug',
    author='Justintime50',
    license='MIT',
    packages=setuptools.find_packages(),
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
    python_requires='>=3.7',
)
