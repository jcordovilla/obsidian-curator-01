#!/usr/bin/env python3
"""
Setup script for Obsidian Curator
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="obsidian-curator",
    version="1.0.0",
    author="Obsidian Curator Team",
    author_email="",
    description="A comprehensive Python application for preprocessing and cleaning Obsidian vaults converted from Evernote",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/obsidian-curator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "obsidian-curator=scripts.preprocess:main",
            "obsidian-analyze=scripts.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json", "*.yaml"],
    },
)
