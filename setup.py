#!/usr/bin/env python3
"""
Setup script for Resume Keyword Optimizer
"""

from setuptools import setup, find_packages
import os

# Read README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="resume-keyword-optimizer",
    version="1.0.0",
    author="Resume Optimizer Team",
    author_email="contact@resumeoptimizer.dev",
    description="A powerful tool to optimize resumes for ATS systems using advanced NLP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/resume-keyword-optimizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "pytest-cov>=2.10.0",
        ],
        "web": [
            "streamlit>=1.28.0",
            "plotly>=5.0.0",
            "wordcloud>=1.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "resume-optimizer=cli:main",
            "resume-optimizer-web=web_app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md"],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/resume-keyword-optimizer/issues",
        "Source": "https://github.com/yourusername/resume-keyword-optimizer",
        "Documentation": "https://github.com/yourusername/resume-keyword-optimizer/wiki",
    },
)