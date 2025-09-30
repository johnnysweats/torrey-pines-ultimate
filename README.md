# Torry Pines Waitlist Automation

This script automates joining the waitlist for Torrey Pines Golf Course.

## Quick Start

1. **First time setup:**
   ```bash
   ./setup.sh
   ```

2. **Run the script:**
   ```bash
   python3 waitlist.py
   ```

3. **Run with caffeinate (prevents computer sleep):**
   ```bash
   caffeinate -i python3 waitlist.py
   ```

## What it does

- Prompts for user information (or uses default for John)
- Asks for course preference (South, North, or First Available)
- Asks for number of players (1-4)
- Asks for target time (24-hour format)
- Waits until the specified time
- Automatically fills out the waitlist form
- Submits the form to join the waitlist

## Requirements

- Python 3.6 or higher
- Chrome browser installed
- Internet connection

## Files

- `waitlist.py` - Main script
- `requirements.txt` - Python dependencies
- `setup.sh` - Setup script for first-time users
- `README.md` - This file

## Troubleshooting

If you get permission errors, try:
```bash
python3 -m pip install --user -r requirements.txt
```

If Chrome doesn't open, make sure Chrome is installed and up to date. 