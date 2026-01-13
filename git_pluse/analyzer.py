"""
GitHub commit analyzer module
"""

import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import defaultdict
import re
from typing import List, Dict, Tuple
import json


class GitHubCommitAnalyzer:

    def __init__(self, github_token: str = None):
        """
        Initialize analyzer
        :param github_token: GitHub Personal Access Token (optional, increases API rate limit)
        """
        self.github_token = github_token
        self.api_base = "https://api.github.com"

    def parse_github_url(self, url: str) -> Tuple[str, str]:
        """Parse GitHub URL to get owner and repo"""
        patterns = [
            r'github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
            r'github\.com/([^/]+)/([^/]+)$',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner, repo = match.groups()
                repo = repo.replace('.git', '')
                return owner, repo

        raise ValueError(f"Cannot parse GitHub URL: {url}")

    def get_commits(self, owner: str, repo: str) -> List[Dict]:
        """Get all commits for the project"""
        commits = []
        page = 1
        per_page = 100

        while True:
            url = f"{self.api_base}/repos/{owner}/{repo}/commits"
            params = {'per_page': per_page, 'page': page, 'state': 'all'}

            headers = {}
            if self.github_token:
                headers['Authorization'] = f'token {self.github_token}'

            try:
                response = requests.get(url, params=params, headers=headers)
                response.raise_for_status()

                data = response.json()

                if not data:
                    break

                commits.extend(data)

                if len(data) < per_page:
                    break

                page += 1

            except requests.exceptions.RequestException as e:
                print(f"Error fetching data: {e}")
                break

        return commits

    def analyze_commit_frequency(self, commits: List[Dict]) -> Dict[str, int]:
        """Analyze commit frequency by date"""
        daily_commits = defaultdict(int)

        for commit in commits:
            commit_date_str = commit.get('commit', {}).get('author', {}).get('date')
            if commit_date_str:
                commit_date = datetime.strptime(commit_date_str, '%Y-%m-%dT%H:%M:%SZ')
                date_str = commit_date.strftime('%Y-%m-%d')
                daily_commits[date_str] += 1

        sorted_commits = dict(sorted(daily_commits.items()))
        return sorted_commits

    def organize_commits_by_date(self, commits: List[Dict]) -> Dict[str, List[Dict]]:
        """Organize commits by date with user and message info"""
        commits_by_date = defaultdict(list)

        for commit in commits:
            commit_date_str = commit.get('commit', {}).get('author', {}).get('date')
            if commit_date_str:
                commit_date = datetime.strptime(commit_date_str, '%Y-%m-%dT%H:%M:%SZ')
                date_str = commit_date.strftime('%Y-%m-%d')

                commit_info = {
                    'user': commit.get('commit', {}).get('author', {}).get('name', 'Unknown'),
                    'message': commit.get('commit', {}).get('message', ''),
                    'sha': commit.get('sha', ''),
                    'time': commit_date_str
                }
                commits_by_date[date_str].append(commit_info)

        sorted_commits = dict(sorted(commits_by_date.items()))
        return sorted_commits

    def determine_time_scale(self, daily_commits: Dict[str, int]) -> str:
        """Determine time scale based on project duration"""
        if not daily_commits:
            return 'daily'

        dates = [datetime.strptime(d, '%Y-%m-%d') for d in daily_commits.keys()]
        start_date = min(dates)
        end_date = max(dates)
        duration_days = (end_date - start_date).days

        if duration_days < 365:
            return 'daily'
        elif duration_days < 3650:
            return 'weekly'
        else:
            return 'quarterly'

    def plot_commit_frequency(
        self,
        daily_commits: Dict[str, int],
        owner: str,
        repo: str,
        save_path: str = None,
        show: bool = False
    ):
        """Plot commit cumulative line chart"""
        if not daily_commits:
            print("No commit data to plot")
            return

        dates = [datetime.strptime(d, '%Y-%m-%d') for d in daily_commits.keys()]
        counts = list(daily_commits.values())

        # Calculate cumulative commit count
        cumulative_counts = []
        cumulative = 0
        for count in counts:
            cumulative += count
            cumulative_counts.append(cumulative)

        # Calculate actual time span (duration days)
        start_date = min(dates)
        end_date = max(dates)
        duration_days = (end_date - start_date).days + 1  # +1 to include both start and end

        fig, ax = plt.subplots(figsize=(14, 7))

        # Plot line chart with markers
        ax.plot(dates, cumulative_counts, linewidth=2, color='#2E86AB',
                marker='o', markersize=4, markerfacecolor='#A23B72',
                markeredgecolor='#A23B72', label='Cumulative Commits')

        # Fill under the line
        ax.fill_between(dates, 0, cumulative_counts, alpha=0.3, color='#2E86AB')

        ax.set_title(f'GitHub Project {owner}/{repo} Cumulative Commits',
                     fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Cumulative Commits', fontsize=12)

        # Determine optimal tick interval based on time duration
        if duration_days <= 30:
            tick_interval = 1
            date_format = '%Y-%m-%d'
        elif duration_days <= 90:
            tick_interval = 7
            date_format = '%Y-%m-%d'
        elif duration_days <= 365:
            tick_interval = 30
            date_format = '%Y-%m'
        elif duration_days <= 730:
            tick_interval = 60
            date_format = '%Y-%m'
        else:
            tick_interval = 90
            date_format = '%Y-%m'

        ax.xaxis.set_major_locator(mdates.DayLocator(interval=tick_interval))
        ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))

        plt.xticks(rotation=45, ha='right')
        ax.grid(True, linestyle='--', alpha=0.7)

        total_commits = sum(counts)
        num_days_with_commits = len(counts)
        avg_commits_per_day = total_commits / duration_days if duration_days > 0 else 0

        stats_text = f'Total Commits: {total_commits}\n' \
                    f'Duration: {duration_days} days\n' \
                    f'Avg/Day: {avg_commits_per_day:.2f}'

        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to: {save_path}")
        elif show:
            plt.show()

        plt.close()

        return daily_commits

    def analyze_repo(self, github_url: str, output_dir: str = ".", show_chart: bool = False):
        """Complete analysis workflow"""
        try:
            owner, repo = self.parse_github_url(github_url)
            print(f"Analyzing project: {owner}/{repo}")

            commits = self.get_commits(owner, repo)

            if not commits:
                print("No commit records found")
                return None

            print(f"Retrieved {len(commits)} commit records")

            daily_commits = self.analyze_commit_frequency(commits)
            commits_by_date = self.organize_commits_by_date(commits)

            # Save JSON file with commit details
            json_filename = f"{repo}.json"
            json_path = f"{output_dir}/{json_filename}"

            result = {
                'repo': f"{owner}/{repo}",
                'url': github_url,
                'total_commits': len(commits),
                'commits_by_date': commits_by_date,
                'first_commit_date': list(commits_by_date.keys())[0] if commits_by_date else None,
                'last_commit_date': list(commits_by_date.keys())[-1] if commits_by_date else None,
            }

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"JSON file saved to: {json_path}")

            # Generate chart if requested
            if show_chart:
                png_filename = f"{repo}.png"
                png_path = f"{output_dir}/{png_filename}"
                self.plot_commit_frequency(daily_commits, owner, repo, save_path=png_path)

            return daily_commits

        except Exception as e:
            print(f"Error during analysis: {e}")
            return None
