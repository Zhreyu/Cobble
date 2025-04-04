"""
Setup script for the File Sorter App.
"""

from setuptools import setup, find_packages

setup(
    name="file_sorter_app",
    version="1.0.0",
    description="A multi-agent file sorting application using Groq API",
    author="Manus AI",
    packages=find_packages(),
    install_requires=[
        "groq>=0.22.0",
        "python-dotenv>=1.1.0",
        "customtkinter>=5.2.0",
    ],
    entry_points={
        "console_scripts": [
            "file-sorter=main:main",
        ],
    },
    python_requires=">=3.8",
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
    ],
)
