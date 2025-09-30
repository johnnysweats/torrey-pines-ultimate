from setuptools import setup

APP = ['golf_waitlist_app_fresh.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'tree_icon.png',
    'plist': {
        'CFBundleName': 'Torrey Pines Waitlist',
        'CFBundleDisplayName': 'Torrey Pines Waitlist',
        'CFBundleGetInfoString': "Torrey Pines Golf Course Waitlist Automation",
        'CFBundleIdentifier': "com.torreypines.waitlist",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHumanReadableCopyright': u"Copyright © 2024, All Rights Reserved"
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
) 