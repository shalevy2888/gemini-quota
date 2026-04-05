# Gemini Quota Taskbar App Implementation Plan

## Background & Motivation
The user requested a macOS taskbar (menu bar) application to monitor the quota usage and reset times of the Gemini CLI models. The application will be built using Python with the `rumps` library (Ridiculously Uncomplicated macOS Python Statusbar apps), which perfectly aligns with the user's preference for managing Python projects via `uv` while providing a true standalone macOS app experience.

## Scope & Impact
- Create a Python-based macOS menu bar app.
- Periodically query the Gemini CLI for the latest session stats.
- Parse the output to extract quota usage percentages and reset times for different model groups.
- Provide a UI in the menu bar to display the worst-case usage among user-selected model groups (Pro, Flash, Flash-Lite).
- Add visual indicators (e.g., colored circles) when usage crosses 60%, 80%, and 90% thresholds.

## Proposed Solution

### 1. Data Fetching & Parsing
The app will run `gemini --output-format json -p "/stats"` as a subprocess every few minutes. It will parse the human-readable table within the JSON response using regular expressions to extract:
- Model Name (e.g., `gemini-2.5-pro`)
- Usage Percentage (e.g., `9%`)
- Reset Time (e.g., `8:46 AM`)

### 2. Grouping & Selection Logic
Models will be categorized into three groups based on their names:
- **Pro:** Contains `pro`
- **Flash:** Contains `flash` (excluding `flash-lite`)
- **Flash-Lite:** Contains `flash-lite`

The user will have a "Settings" menu to toggle which groups they want to monitor.
If the user selects multiple groups, the app will display the stats for the model with the **highest usage percentage** (the "worst" case) in the menu bar.

### 3. UI and Visual Indicators
The menu bar title will display the worst usage and its reset time (e.g., `🔴 92% | 8:46 AM`).
Severity indicators will be used:
- 🟢 `< 60%`
- 🟡 `>= 60%`
- 🟠 `>= 80%`
- 🔴 `>= 90%`

Clicking the menu bar icon will reveal a dropdown menu showing:
- The full parsed stats for all models (as individual, non-clickable menu items).
- A "Settings" submenu with toggleable checkmarks for "Monitor Pro", "Monitor Flash", and "Monitor Flash-Lite".
- A "Refresh Now" button to manually trigger an update.
- A "Quit" button.

### 4. Project Setup
We will use `uv` to create and manage the environment, installing `rumps` for the app logic.

## Alternatives Considered
- **SwiftBar/xbar Script:** Easier to write but requires installing a third-party host application. The user explicitly chose the standalone Python (`rumps`) approach.
- **Native Swift/SwiftUI:** Provides the most native experience but is more complex to maintain compared to a simple Python script managed by `uv`.

## Implementation Steps
1. Initialize the project directory and environment using `uv init`.
2. Add `rumps` dependency: `uv add rumps`.
3. Create `app.py` containing the `rumps.App` subclass.
4. Implement the `subprocess` call to fetch Gemini CLI stats.
5. Implement the RegEx parsing logic for the quota table.
6. Build the dynamic menu and update loop using `@rumps.timer`.
7. Test the application locally.

## Verification
- Verify the app launches and appears in the macOS menu bar.
- Verify it correctly parses the stats from the Gemini CLI.
- Verify the group toggling logic correctly identifies and displays the worst-case model.
- Verify the visual indicators update correctly based on the simulated or actual usage percentages.