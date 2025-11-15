#!/usr/bin/env python3
import subprocess
import json
import base64
import sys
import os

# Get the repository directory (where this script is located)
repo_dir = os.path.dirname(os.path.abspath(__file__))

# Get all commits
result = subprocess.run(
    ['git', 'log', '--all', '--format=%H|%s|%ai|%an', '--', 'index.html', 'clickhouse_team_activity.html'],
    capture_output=True,
    text=True,
    cwd=repo_dir
)

commits = []
for line in result.stdout.strip().split('\n'):
    if not line or '|' not in line:
        continue

    parts = line.split('|', 3)
    commit_hash = parts[0].strip()
    message = parts[1].strip() if len(parts) > 1 else ''
    date = parts[2].strip() if len(parts) > 2 else ''
    author = parts[3].strip() if len(parts) > 3 else ''

    # Try both filenames
    content = None
    for filename in ['index.html', 'clickhouse_team_activity.html']:
        file_result = subprocess.run(
            ['git', 'show', f'{commit_hash}:{filename}'],
            capture_output=True,
            text=True,
            cwd=repo_dir
        )

        if file_result.returncode == 0:
            content = file_result.stdout
            break

    if content:
        content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        commits.append({
            'hash': commit_hash,
            'message': message,
            'date': date,
            'author': author,
            'content': content_b64
        })
        print(f'Processed {len(commits)}: {message[:60]}', file=sys.stderr)
    else:
        print(f'SKIPPED {commit_hash[:8]}: {message[:60]} (file not found)', file=sys.stderr)

# Reverse to go from oldest to newest
commits.reverse()

print(f'\nTotal commits: {len(commits)}', file=sys.stderr)

# Write to .commits_data.json
output_file = os.path.join(repo_dir, '.commits_data.json')
with open(output_file, 'w') as f:
    json.dump(commits, f, indent=2)

print(f'Saved to {output_file}', file=sys.stderr)
