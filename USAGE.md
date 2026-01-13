# git-pluse Usage Guide

## Installation

### From PyPI (after publishing)

```bash
pip install git-pluse
```

### From Source

```bash
git clone <repository-url>
cd git-pluse
pip install -e .
```

## Command Line Usage

### Basic Syntax

```bash
git-pluse <github_url> [show] [options]
```

### Examples

#### 1. Generate JSON output only

```bash
git-pluse https://github.com/python/cpython
```

Output: Creates `cpython.json` in the current directory

#### 2. Generate JSON and PNG chart

```bash
git-pluse https://github.com/python/cpython show
```

Output: Creates both `cpython.json` and `cpython.png`

#### 3. Specify output directory

```bash
git-pluse https://github.com/python/cpython -o /path/to/output
git-pluse https://github.com/python/cpython show -o /path/to/output
```

#### 4. Use GitHub Token (for higher rate limits)

```bash
git-pluse https://github.com/python/cpython --token ghp_your_token_here
```

## Output Format

### JSON File Structure

```json
{
  "repo": "owner/repo",
  "url": "https://github.com/owner/repo",
  "total_commits": 1234,
  "commit_frequency": {
    "2024-01-01": 5,
    "2024-01-02": 3,
    ...
  },
  "first_commit_date": "2020-01-01",
  "last_commit_date": "2024-12-31"
}
```

### PNG Chart

The chart visualizes commit frequency over time with:
- Line graph showing daily commit counts
- Filled area under the line
- Statistics box showing:
  - Total commits
  - Average commits per day
  - Peak commit day

### Time Scale Adaptation

The x-axis ticks adapt based on project duration:

- **< 1 year**: Daily ticks (each day shown)
- **1-10 years**: Weekly ticks (Mondays shown)
- **> 10 years**: Quarterly ticks (Jan, Apr, Jul, Oct shown)

## GitHub Token (Optional)

### Why Use a Token?

GitHub's API has rate limits:
- Without token: 60 requests/hour
- With token: 5000 requests/hour

### How to Get a Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Select scopes: `public_repo` (for public repositories)
4. Generate and copy the token

### Usage

```bash
git-pluse https://github.com/owner/repo --token ghp_xxxxxxxxxxxx
```

Or set as environment variable:

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
git-pluse https://github.com/owner/repo --token $GITHUB_TOKEN
```

## API Usage

You can also use the library programmatically:

```python
from git_pluse import GitHubCommitAnalyzer

# Initialize analyzer
analyzer = GitHubCommitAnalyzer(github_token="your_token_here")

# Analyze a repository
daily_commits = analyzer.analyze_repo(
    "https://github.com/owner/repo",
    output_dir="./output",
    show_chart=True
)

print(f"Total commit days: {len(daily_commits)}")
```

## Troubleshooting

### Rate Limit Exceeded

```
Error: 403 Client Error: rate limit exceeded
```

Solution: Use a GitHub token with `--token` option

### Font Warnings

```
UserWarning: Glyph missing from font
```

This is harmless for English environments. For Chinese environments, ensure SimHei font is installed.

### No Commits Found

```
No commit records found
```

Check that:
- The repository URL is correct
- The repository is public (or use a token with appropriate permissions)

## Examples

### Analyze a small project

```bash
git-pluse https://github.com/yourusername/small-project show
```

### Analyze a large project with token

```bash
git-pluse https://github.com/torvalds/linux show --token ghp_your_token
```

### Batch analyze multiple projects

```bash
#!/bin/bash
repos=(
  "https://github.com/python/cpython"
  "https://github.com/v8/v8"
  "https://github.com/nodejs/node"
)

for repo in "${repos[@]}"; do
  git-pluse "$repo" show -o ./results
done
```

## Performance Notes

- Small projects (< 1000 commits): < 10 seconds
- Medium projects (1000-10000 commits): 10-60 seconds
- Large projects (> 10000 commits): May take several minutes

Consider using a GitHub token for large projects to avoid rate limiting.
