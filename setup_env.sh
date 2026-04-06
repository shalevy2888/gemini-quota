#!/bin/bash
set -e

echo "🚀 Starting Gemini Quota setup..."

# 1. Check for uv
if ! command -v uv &> /dev/null; then
    echo "❌ 'uv' is not installed. Please install it first: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# 2. Ensure Python 3.12 environment
echo "📦 Creating virtual environment with Python 3.12..."
uv venv --python 3.12

# 3. Sync dependencies
echo "📦 Installing dependencies..."
uv sync

# 4. Apply Python 3.12 patches to py2app
echo "patching py2app for Python 3.12 compatibility..."

PY2APP_BUILD_FILE=".venv/lib/python3.12/site-packages/py2app/build_app.py"

if [ -f "$PY2APP_BUILD_FILE" ]; then
    # Fix 'install_requires' error
    sed -i '' 's/raise DistutilsOptionError("install_requires is no longer supported")/pass/g' "$PY2APP_BUILD_FILE"
    
    # Fix 'zlib' error (crucial for Python 3.12 builds)
    sed -i '' 's/self.copy_file(zlib.__file__, os.path.dirname(arcdir))/if hasattr(zlib, "__file__"): self.copy_file(zlib.__file__, os.path.dirname(arcdir))/g' "$PY2APP_BUILD_FILE"
    
    echo "✅ Patches applied successfully."
else
    echo "⚠️ Warning: Could not find py2app build file to patch at $PY2APP_BUILD_FILE."
    echo "Build might fail if the path is different in your environment."
fi

echo "✨ Setup complete! You can now run the app or build it."
echo "👉 Run directly: uv run python app.py"
echo "👉 Build .app:   sh rebuild.sh"
