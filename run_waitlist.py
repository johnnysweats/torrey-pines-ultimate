#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple launcher for Torrey Pines Waitlist Automation
"""

import os
import sys
import subprocess

def main():
    print("🏌️  Torrey Pines Waitlist Automation")
    print("=" * 40)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Virtual environment not detected.")
        print("Run: source venv/bin/activate")
        print()
    
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    waitlist_path = os.path.join(script_dir, "waitlist.py")
    
    # Run with sleep prevention automatically using subprocess for better path handling
    try:
        subprocess.run(["caffeinate", "-i", sys.executable, waitlist_path], check=True)
    except subprocess.CalledProcessError as e:
        print("Error running waitlist script: {}".format(e))
        sys.exit(1)

if __name__ == "__main__":
    main() 