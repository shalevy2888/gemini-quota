#!/bin/bash
# Clean up old builds
echo "Cleaning up..."
rm -rf build dist

# Check if py2app is patched (simple check for the zlib fix)
if ! grep -q "hasattr(zlib" .venv/lib/python3.12/site-packages/py2app/build_app.py; then
    echo "Patching py2app for Python 3.12 compatibility..."
    sed -i '' 's/raise DistutilsOptionError("install_requires is no longer supported")/pass/g' .venv/lib/python3.12/site-packages/py2app/build_app.py
    sed -i '' 's/self.copy_file(zlib.__file__, os.path.dirname(arcdir))/if hasattr(zlib, "__file__"): self.copy_file(zlib.__file__, os.path.dirname(arcdir))/g' .venv/lib/python3.12/site-packages/py2app/build_app.py
fi

# Build the app
echo "Building Gemini Quota.app..."
uv run python setup.py py2app

echo "Done! You can find the app in the 'dist' folder."
