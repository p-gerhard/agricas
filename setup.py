from setuptools import setup, find_packages

setup(
    name="agricas",
    version="0.2.0",
    author="Pierre Gerhard",
    author_email="pierre.gerhard@gmail.com",
    license="MIT",
    description="Web scraper for the URL http://www.agricas.fr/menu-au-ria.",
    long_description_content_type="text/markdown",
    url="https://github.com/p-gerhard/agricas",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        "beautifulsoup4",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "agricas = agricas.agricas:main",
        ],
    },
)
