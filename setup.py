from setuptools import setup

APP = ['thinker.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'plist': 'Info.plist',
    'packages': ['rumps', 'pynput'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
