#!/usr/bin/env python3
"""Main entry point for RiskLens AI"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.cli import main

if __name__ == '__main__':
    main()

