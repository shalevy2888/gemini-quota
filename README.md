# Gemini Quota Taskbar App

A macOS menu bar application to monitor your Gemini CLI quota usage and reset times in real-time.

## Features
- Displays highest usage percentage and reset time in the menu bar.
- Color-coded severity indicators (🟢, 🟡, 🟠, 🔴).
- Detailed breakdown of all models in the dropdown menu.
- Customizable monitoring groups (Pro, Flash, Flash-Lite).
- Automatic token refreshing using your existing Gemini CLI credentials.

## Requirements
- macOS
- Gemini CLI (logged in via `gemini login`)
- Python 3.12+
- `uv` for package management

## Installation & Build
To build the standalone `.app`:
```bash
sh rebuild.sh
```
The application will be created in the `dist/` folder.

## Running from Source
```bash
uv run python app.py
```
