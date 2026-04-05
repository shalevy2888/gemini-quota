from setuptools import setup

APP = ['app.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'compressed': 0,
    'plist': {
        'LSUIElement': True,
        'CFBundleName': "Gemini Quota",
        'CFBundleDisplayName': "Gemini Quota",
        'CFBundleIdentifier': "com.shaylevy.gemini-quota",
    },
    'packages': ['rumps', 'requests', 'charset_normalizer', 'idna', 'urllib3', 'certifi'],
    'includes': ['rumps', 'requests', 'charset_normalizer', 'idna', 'urllib3', 'certifi'],
}

setup(
    name='GeminiQuotaApp',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
)
