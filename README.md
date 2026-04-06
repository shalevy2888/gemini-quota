# Gemini Quota Taskbar App

![Gemini Quota Menu Bar](icons/Gemini%20Quota%20MenuBar.png)

A macOS menu bar application to monitor your Gemini CLI quota usage and reset times in real-time.

## Features
- **Custom Icons:** Visual severity indicators using custom PNGs.
- **Usage Overview:** Quick view of Pro and Flash usage directly in the menu.
- **Relative Resets:** See exactly how many hours/minutes until your quota resets.
- **Persistent Settings:** Remembers your display preferences and refresh rates.
- **Auto-Refresh:** Configurable refresh rates (60s, 120s, 300s).
- **One-Click Login:** Refresh your Gemini CLI authentication directly from the menu.

## Prerequisites
- **macOS**
- **Gemini CLI:** Must be installed and logged in (`gemini login`).
- **uv:** Fast Python package manager. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd gemini_quota
   ```

2. **Prepare Icons:**
   Ensure you have PNG icons in the `icons/` folder named:
   `green.png`, `yellow.png`, `orange.png`, `red.png`, `gray.png`.

3. **Run the setup script:**
   This will create the virtual environment, install dependencies, and apply necessary patches for Python 3.12 compatibility.
   ```bash
   sh setup_env.sh
   ```

## Running the App

### Option A: Run from Source (Terminal required)
```bash
uv run python app.py
```

### Option B: Build a Native macOS App
To create a standalone `.app` that doesn't require an open terminal:
```bash
sh rebuild.sh
```
The finished application will be in the `dist/Gemini Quota.app` folder.

## Troubleshooting
- **⚠️ Relogin:** If the app shows a relogin warning, use the **Login / Refresh Auth** menu item to re-authenticate with Google.
- **Icons not showing:** Ensure the `icons/` folder exists and contains the required PNG files.
