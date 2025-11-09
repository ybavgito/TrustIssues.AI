"""Setup script for RiskLens AI"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="risklens-ai",
    version="1.0.0",
    author="RiskLens Team",
    description="Automated vendor onboarding with agentic workflow and risk assessment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "openai>=1.0.0",
        "pydantic>=2.0.0",
        "pypdf2>=3.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "fuzzywuzzy>=0.18.0",
        "python-Levenshtein>=0.21.0",
        "colorama>=0.4.6",
        "tabulate>=0.9.0",
        "reportlab>=4.0.0",
        "python-dateutil>=2.8.0",
    ],
    entry_points={
        "console_scripts": [
            "risklens=src.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

