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
    version='1.3.0',
    description='Pull Bug is great at bugging you to merge or close your pull/merge requests.',
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
            'pylint >= 2.5.0',
        ]
    },
    python_requires='>=3.6',
)
