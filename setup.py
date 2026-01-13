from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="git-pluse",
    version="1.0.0",
    author="erquren",
    author_email="contact@erquren.com",
    description="GitHub commit analyzer - analyze and visualize commit frequency",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/erquren/git-pluse",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "matplotlib>=3.3.0",
    ],
    entry_points={
        "console_scripts": [
            "git-pluse=git_pluse.cli:main",
        ],
    },
)
