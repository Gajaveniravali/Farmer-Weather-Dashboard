#!/usr/bin/env python
"""Entry point for Farmer Weather Dashboard."""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app

if __name__ == '__main__':
    app.run(debug=True)
