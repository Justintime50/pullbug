import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

REQUIREMENTS = [
    'requests >= 1.0.0',
    'slackclient >= 2.0.1',
    'python-dotenv >= 0.10.0'
]

setuptools.setup(
    name='pullbug',
    version='2.0.4',
    description='Get bugged via Slack or RocketChat to merge your GitHub pull requests or GitLab merge requests.',  # noqa
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
        'dev': [
            'pytest >= 6.0.0',
            'pytest-cov >= 2.10.0',
            'coveralls >= 2.1.2',
            'flake8 >= 3.8.0',
            'mock >= 4.0.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'pullbug=pullbug.cli:main'
        ]
    },
    python_requires='>=3.6',
)
