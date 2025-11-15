#!/usr/bin/env python3
import json
import sys
import os

# Get the repository directory (where this script is located)
repo_dir = os.path.dirname(os.path.abspath(__file__))
commits_file = os.path.join(repo_dir, '.commits_data.json')
output_file = os.path.join(repo_dir, 'history', 'index.html')

# Read the commits data
with open(commits_file, 'r') as f:
    commits = json.load(f)

print(f'Loaded {len(commits)} commits', file=sys.stderr)

# Create the HTML viewer
html_start = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Index.html Commit History Viewer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            overflow: hidden;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        #nav-bar {
            background: #2c3e50;
            color: white;
            padding: 15px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 100;
            flex-shrink: 0;
        }

        #commit-info {
            flex: 1;
            margin: 0 20px;
        }

        #commit-message {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 4px;
        }

        #commit-meta {
            font-size: 12px;
            opacity: 0.8;
        }

        #nav-controls {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        button {
            background: #34495e;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: background 0.2s;
        }

        button:hover:not(:disabled) {
            background: #4a5f7f;
        }

        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        #counter {
            background: #34495e;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: 600;
            min-width: 100px;
            text-align: center;
        }

        #content-frame {
            flex: 1;
            border: none;
            background: white;
        }

        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            font-size: 20px;
            color: #666;
        }

        .keyboard-hint {
            font-size: 11px;
            opacity: 0.7;
            margin-top: 2px;
        }
    </style>
</head>
<body>
    <div id="nav-bar">
        <div id="nav-controls">
            <button id="prev-btn" onclick="navigate(-1)">← Previous</button>
            <div id="counter">1 / ''' + str(len(commits)) + '''</div>
            <button id="next-btn" onclick="navigate(1)">Next →</button>
        </div>
        <div id="commit-info">
            <div id="commit-message"></div>
            <div id="commit-meta"></div>
            <div class="keyboard-hint">Use ← → arrow keys or swipe to navigate</div>
        </div>
    </div>
    <iframe id="content-frame"></iframe>

    <script>
        // Embed all commits data
        const COMMITS = '''

html_end = ''';

        let currentIndex = 0;
        let currentBlobUrl = null;

        // Proper UTF-8 base64 decoding
        function base64DecodeUnicode(str) {
            // Convert base64 to percent-encoding, then decode
            const percentEncodedStr = atob(str).split('').map(function(c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join('');
            return decodeURIComponent(percentEncodedStr);
        }

        // Build localStorage polyfill script using string concatenation
        const polyfillScript = '<' + 'script>' +
            '(function() {' +
            '  try {' +
            '    var test = window.localStorage;' +
            '    test.setItem("__test__", "1");' +
            '    test.removeItem("__test__");' +
            '  } catch (e) {' +
            '    var storage = {};' +
            '    Object.defineProperty(window, "localStorage", {' +
            '      value: {' +
            '        getItem: function(key) { return storage.hasOwnProperty(key) ? storage[key] : null; },' +
            '        setItem: function(key, value) { storage[key] = String(value); },' +
            '        removeItem: function(key) { delete storage[key]; },' +
            '        clear: function() { storage = {}; },' +
            '        key: function(i) { var keys = Object.keys(storage); return keys[i] || null; },' +
            '        get length() { return Object.keys(storage).length; }' +
            '      },' +
            '      writable: false,' +
            '      configurable: false' +
            '    });' +
            '  }' +
            '})();' +
            '<' + '/script>';

        function updateFavicon(html) {
            // Extract favicon from HTML
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const faviconLink = doc.querySelector('link[rel*="icon"]');

            // Remove existing favicon
            const existingFavicon = document.querySelector('link[rel*="icon"]');
            if (existingFavicon) {
                existingFavicon.remove();
            }

            // Add new favicon if exists
            if (faviconLink) {
                const newFavicon = document.createElement('link');
                newFavicon.rel = faviconLink.rel;
                newFavicon.type = faviconLink.type;
                newFavicon.href = faviconLink.href;
                document.head.appendChild(newFavicon);
            }
        }

        function renderCommit(index) {
            if (index < 0 || index >= COMMITS.length) return;

            currentIndex = index;
            const commit = COMMITS[index];

            // Update UI
            document.getElementById('commit-message').textContent = commit.message;
            document.getElementById('commit-meta').textContent =
                `${commit.author} · ${commit.date} · ${commit.hash.substring(0, 8)}`;
            document.getElementById('counter').textContent = `${index + 1} / ${COMMITS.length}`;

            // Update navigation buttons
            document.getElementById('prev-btn').disabled = index === 0;
            document.getElementById('next-btn').disabled = index === COMMITS.length - 1;

            // Decode content with proper UTF-8 handling
            let content = base64DecodeUnicode(commit.content);

            // Inject localStorage polyfill as THE VERY FIRST THING after opening <html> tag
            content = content.replace(/(<html[^>]*>)/i, '$1\\n' + polyfillScript);

            const iframe = document.getElementById('content-frame');

            // Update favicon from this version
            updateFavicon(content);

            // Update document title
            const parser = new DOMParser();
            const doc = parser.parseFromString(content, 'text/html');
            const title = doc.querySelector('title');
            if (title) {
                document.title = `[${index + 1}/${COMMITS.length}] ${title.textContent}`;
            }

            // Revoke previous blob URL to free memory
            if (currentBlobUrl) {
                URL.revokeObjectURL(currentBlobUrl);
            }

            // Create a new blob URL and load it in the iframe
            const blob = new Blob([content], { type: 'text/html; charset=utf-8' });
            currentBlobUrl = URL.createObjectURL(blob);
            iframe.src = currentBlobUrl;
        }

        function navigate(delta) {
            const newIndex = currentIndex + delta;
            if (newIndex >= 0 && newIndex < COMMITS.length) {
                renderCommit(newIndex);
            }
        }

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                e.preventDefault();
                navigate(-1);
            } else if (e.key === 'ArrowRight') {
                e.preventDefault();
                navigate(1);
            } else if (e.key === 'Home') {
                e.preventDefault();
                renderCommit(0);
            } else if (e.key === 'End') {
                e.preventDefault();
                renderCommit(COMMITS.length - 1);
            }
        });

        // Touch/swipe support
        let touchStartX = 0;
        let touchEndX = 0;

        document.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        });

        document.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        });

        function handleSwipe() {
            const swipeThreshold = 50;
            const diff = touchStartX - touchEndX;

            if (Math.abs(diff) > swipeThreshold) {
                if (diff > 0) {
                    // Swipe left - next
                    navigate(1);
                } else {
                    // Swipe right - previous
                    navigate(-1);
                }
            }
        }

        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            if (currentBlobUrl) {
                URL.revokeObjectURL(currentBlobUrl);
            }
        });

        // Initial render
        renderCommit(0);
    </script>
</body>
</html>
'''

# Write the output
with open(output_file, 'w') as f:
    f.write(html_start)
    f.write(json.dumps(commits))
    f.write(html_end)

print(f'Created history/index.html ({len(html_start) + len(html_end) + len(json.dumps(commits))} bytes)', file=sys.stderr)
