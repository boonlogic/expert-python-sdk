from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='boonnano',
    version='3.0.2',
    author="BoonLogic",
    author_email="elise@boonlogic.com",
    packages=['boonnano'],
    description="A SDK package for utilizing the BoonLogic nano API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/boonlogic/Python_API",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ]
)
