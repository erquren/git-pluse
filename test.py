import requests
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import defaultdict
import re
from typing import List, Dict


class GitHubCommitAnalyzer:

    def __init__(self, github_token: str = None):
        """
        Initialize analyzer
        :param github_token: GitHub Personal Access Token (optional, increases API rate limit)
        """
        self.github_token = github_token
        self.api_base = "https://api.github.com"

    def parse_github_url(self, url: str) -> tuple:
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

        print(f"Fetching commit data for {owner}/{repo}...")

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
                print(f"Fetched {len(commits)} commit records...")

                # Check if there are more data
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

    def plot_commit_frequency(self,
                              daily_commits: Dict[str, int],
                              owner: str,
                              repo: str,
                              save_path: str = None):
        """Plot commit frequency line chart"""
        if not daily_commits:
            print("No commit data to plot")
            return

        dates = [
            datetime.strptime(d, '%Y-%m-%d') for d in daily_commits.keys()
        ]
        counts = list(daily_commits.values())

        fig, ax = plt.subplots(figsize=(14, 7))

        ax.plot(dates,
                counts,
                linewidth=2,
                color='#2E86AB',
                marker='o',
                markersize=4,
                markerfacecolor='#A23B72',
                markeredgecolor='#A23B72')

        ax.fill_between(dates, counts, alpha=0.3, color='#2E86AB')

        ax.set_title(f'GitHub Project {owner}/{repo} Commit Frequency',
                     fontsize=16,
                     fontweight='bold',
                     pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Commit Count', fontsize=12)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())

        plt.xticks(rotation=45, ha='right')

        ax.grid(True, linestyle='--', alpha=0.7)

        total_commits = sum(counts)
        avg_commits = total_commits / len(counts) if counts else 0
        max_commits = max(counts) if counts else 0
        max_date = list(daily_commits.keys())[counts.index(
            max_commits)] if counts else "N/A"

        stats_text = f'Total Commits: {total_commits}\n' \
                    f'Avg Commits/Day: {avg_commits:.2f}\n' \
                    f'Peak: {max_commits} (Date: {max_date})'

        ax.text(0.02,
                0.98,
                stats_text,
                transform=ax.transAxes,
                fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to: {save_path}")
        else:
            plt.show()

        return daily_commits

    def analyze_repo(self, github_url: str, save_path: str = None):
        """Complete analysis workflow"""
        try:
            owner, repo = self.parse_github_url(github_url)
            print(f"Analyzing project: {owner}/{repo}")

            commits = self.get_commits(owner, repo)

            if not commits:
                print("No commit records found")
                return

            print(f"Retrieved {len(commits)} commit records")

            daily_commits = self.analyze_commit_frequency(commits)

            self.plot_commit_frequency(daily_commits, owner, repo, save_path)

            return daily_commits

        except Exception as e:
            print(f"Error during analysis: {e}")
            return None


def main():
    """Main function"""
    # Optional: Set GitHub Token to increase API limit
    # Get token at: https://github.com/settings/tokens
    GITHUB_TOKEN = None  # Replace with your token, e.g., "ghp_xxxxxxxxxxxx"

    # Input GitHub project URL
    github_url = input("Enter GitHub project URL: ").strip()

    # Optional: Specify save path
    save_path = input("Enter save path (leave empty to show chart): ").strip() or None

    # Create analyzer and execute analysis
    analyzer = GitHubCommitAnalyzer(github_token=GITHUB_TOKEN)
    daily_commits = analyzer.analyze_repo(github_url, save_path)

    if daily_commits:
        print("\nAnalysis completed!")
        print(f"Total {len(daily_commits)} days with commit records")


if __name__ == "__main__":
    main()
