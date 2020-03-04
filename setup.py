import setuptools

with open("README.md", "r", encoding='utf8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymirai", 
    version="0.0.3",
    author="0h2o",
    author_email="yype@foxmail.com",
    description="A simple python binding for the great project Mirai",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/0h2o/pymirai",
    packages=setuptools.find_packages(),
    install_requires=[
        'aiohttp>=3.6.2'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7.1',
)