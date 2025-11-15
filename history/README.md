# Commit History Viewer

Interactive viewer for navigating the commit history of `index.html`.

## Files

- **`history/index.html`** - The main viewer (8.1 MB, self-contained single-page application)
- **`extract_commits_data.py`** - Extract all commits that changed index.html into `.commits_data.json`
- **`generate_history_viewer.py`** - Generate `history/index.html` from `.commits_data.json`
- **`.commits_data.json`** - All commit data in JSON format (7.5 MB)

## Usage

Just open `history/index.html` in your browser to view the commit history interactively.

### Navigation

- **Previous/Next buttons** - Navigate between commits
- **Arrow keys (← →)** - Navigate with keyboard
- **Home/End keys** - Jump to first/last commit
- **Swipe left/right** - Navigate on mobile devices

## Regenerating the viewer

If you want to update the viewer with new commits:

1. Extract fresh commit data:
   ```bash
   ./extract_commits_data.py
   ```

2. Generate the viewer:
   ```bash
   ./generate_history_viewer.py
   ```

## Technical Details

- Tracks file history including rename from `clickhouse_team_activity.html` to `index.html`
- Uses blob URLs to avoid same-origin policy issues
- Includes localStorage polyfill for restricted contexts
- Proper UTF-8/emoji handling with base64 encoding
- All commit versions embedded in a single file for portability
