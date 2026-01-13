# git-pluse

A GitHub commit analyzer that fetches commit history and visualizes cumulative commits over time.

## Installation

```bash
pip install git-pluse
```

## Usage

### Basic usage - generate JSON output

```bash
git-pluse https://github.com/owner/repo
```

This will create a JSON file named `repo.json` containing detailed commit records organized by date.

### Generate visualization

```bash
git-pluse https://github.com/owner/repo show
```

This will create both a JSON file (`repo.json`) and a PNG chart (`repo.png`) showing cumulative commits.

## Features

- Fetches all commits from a GitHub repository
- Generates JSON output with commit details (user, message, sha, time) organized by date
- Visualizes cumulative commits over time with line chart
- Dynamic tick intervals based on actual project duration:
  - ≤ 30 days: daily ticks
  - ≤ 90 days: weekly ticks
  - ≤ 365 days: monthly ticks
  - ≤ 730 days: bi-monthly ticks
  - > 730 days: quarterly ticks

## JSON Output Format

```json
{
  "repo": "owner/repo",
  "url": "https://github.com/owner/repo",
  "total_commits": 1234,
  "commits_by_date": {
    "2024-01-01": [
      {
        "user": "John Doe",
        "message": "Initial commit",
        "sha": "abc123...",
        "time": "2024-01-01T12:00:00Z"
      }
    ]
  },
  "first_commit_date": "2024-01-01",
  "last_commit_date": "2024-12-31"
}
```

## Chart Features

- **X-axis**: Date
- **Y-axis**: Cumulative commit count
- Dynamic tick intervals based on project duration
- Clean line chart with data point markers
- Area fill for better visualization

## Requirements

- Python 3.7+
- requests
- matplotlib

## License

MIT License
