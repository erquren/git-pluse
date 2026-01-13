"""
Unit tests for GitHubCommitAnalyzer
Tests cover all methods with edge cases, mocking, and comprehensive coverage
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from collections import defaultdict
import requests

from test import GitHubCommitAnalyzer


class TestGitHubCommitAnalyzerInit:
    """Test cases for __init__ method"""

    def test_init_with_token(self):
        """Test initialization with GitHub token"""
        analyzer = GitHubCommitAnalyzer(github_token="test_token")
        assert analyzer.github_token == "test_token"
        assert analyzer.api_base == "https://api.github.com"

    def test_init_without_token(self):
        """Test initialization without GitHub token"""
        analyzer = GitHubCommitAnalyzer()
        assert analyzer.github_token is None
        assert analyzer.api_base == "https://api.github.com"


class TestParseGitHubUrl:
    """Test cases for parse_github_url method"""

    @pytest.mark.parametrize("url,expected_owner,expected_repo", [
        ("https://github.com/owner/repo", "owner", "repo"),
        ("https://github.com/owner/repo.git", "owner", "repo"),
        ("https://github.com/owner/repo/", "owner", "repo"),
        ("https://github.com/owner/repo.git/", "owner", "repo"),
        ("http://github.com/owner/repo", "owner", "repo"),
        ("github.com/owner/repo", "owner", "repo"),
    ])
    def test_parse_valid_urls(self, url, expected_owner, expected_repo):
        """Test parsing various valid GitHub URL formats"""
        analyzer = GitHubCommitAnalyzer()
        owner, repo = analyzer.parse_github_url(url)
        assert owner == expected_owner
        assert repo == expected_repo

    def test_parse_url_with_special_characters(self):
        """Test parsing URL with hyphens and numbers in repo name"""
        analyzer = GitHubCommitAnalyzer()
        owner, repo = analyzer.parse_github_url("https://github.com/my-org/my-repo-123")
        assert owner == "my-org"
        assert repo == "my-repo-123"

    @pytest.mark.parametrize("invalid_url", [
        "https://notgithub.com/owner/repo",
        "https://github.com/owner",
        "https://github.com/",
        "invalid-url",
        "",
        "https://github.com/owner/repo/extra/path",
    ])
    def test_parse_invalid_urls(self, invalid_url):
        """Test parsing invalid URLs raises ValueError"""
        analyzer = GitHubCommitAnalyzer()
        with pytest.raises(ValueError, match="Cannot parse GitHub URL"):
            analyzer.parse_github_url(invalid_url)


class TestGetCommits:
    """Test cases for get_commits method"""

    @patch('test.requests.get')
    def test_get_commits_success_single_page(self, mock_get):
        """Test successful commit retrieval with single page"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                'sha': 'abc123',
                'commit': {
                    'author': {'date': '2024-01-01T12:00:00Z'}
                }
            }
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        analyzer = GitHubCommitAnalyzer()
        commits = analyzer.get_commits('owner', 'repo')

        assert len(commits) == 1
        mock_get.assert_called_once()

    @patch('test.requests.get')
    def test_get_commits_success_multiple_pages(self, mock_get):
        """Test successful commit retrieval with multiple pages"""
        # First page with 100 commits
        mock_response1 = Mock()
        mock_response1.json.return_value = [
            {
                'sha': f'sha{i}',
                'commit': {
                    'author': {'date': '2024-01-01T12:00:00Z'}
                }
            } for i in range(100)
        ]
        mock_response1.raise_for_status = Mock()

        # Second page with 50 commits
        mock_response2 = Mock()
        mock_response2.json.return_value = [
            {
                'sha': f'sha{i}',
                'commit': {
                    'author': {'date': '2024-01-01T12:00:00Z'}
                }
            } for i in range(100, 150)
        ]
        mock_response2.raise_for_status = Mock()

        mock_get.side_effect = [mock_response1, mock_response2]

        analyzer = GitHubCommitAnalyzer()
        commits = analyzer.get_commits('owner', 'repo')

        assert len(commits) == 150
        assert mock_get.call_count == 2

    @patch('test.requests.get')
    def test_get_commits_with_token(self, mock_get):
        """Test commit retrieval with authentication token"""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        analyzer = GitHubCommitAnalyzer(github_token="test_token")
        analyzer.get_commits('owner', 'repo')

        call_kwargs = mock_get.call_args.kwargs
        assert 'headers' in call_kwargs
        assert call_kwargs['headers']['Authorization'] == 'token test_token'

    @patch('test.requests.get')
    def test_get_commits_without_token(self, mock_get):
        """Test commit retrieval without authentication token"""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        analyzer = GitHubCommitAnalyzer()
        analyzer.get_commits('owner', 'repo')

        call_kwargs = mock_get.call_args.kwargs
        assert 'headers' not in call_kwargs or call_kwargs['headers'] == {}

    @patch('test.requests.get')
    def test_get_commits_empty_response(self, mock_get):
        """Test commit retrieval with empty response"""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        analyzer = GitHubCommitAnalyzer()
        commits = analyzer.get_commits('owner', 'repo')

        assert len(commits) == 0

    @patch('test.requests.get')
    def test_get_commits_request_exception(self, mock_get):
        """Test commit retrieval handles request exceptions"""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        analyzer = GitHubCommitAnalyzer()
        commits = analyzer.get_commits('owner', 'repo')

        assert len(commits) == 0

    @patch('test.requests.get')
    def test_get_commits_http_error(self, mock_get):
        """Test commit retrieval handles HTTP errors"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        analyzer = GitHubCommitAnalyzer()
        commits = analyzer.get_commits('owner', 'repo')

        assert len(commits) == 0

    @patch('test.requests.get')
    def test_get_commits_pagination_params(self, mock_get):
        """Test that correct pagination parameters are sent"""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        analyzer = GitHubCommitAnalyzer()
        analyzer.get_commits('owner', 'repo')

        call_args = mock_get.call_args
        assert 'params' in call_args.kwargs
        assert call_args.kwargs['params']['per_page'] == 100
        assert call_args.kwargs['params']['page'] == 1


class TestAnalyzeCommitFrequency:
    """Test cases for analyze_commit_frequency method"""

    def test_analyze_empty_commits(self):
        """Test analyzing empty commit list"""
        analyzer = GitHubCommitAnalyzer()
        result = analyzer.analyze_commit_frequency([])

        assert result == {}
        assert isinstance(result, dict)

    def test_analyze_single_commit(self):
        """Test analyzing single commit"""
        analyzer = GitHubCommitAnalyzer()
        commits = [
            {
                'sha': 'abc123',
                'commit': {
                    'author': {'date': '2024-01-01T12:00:00Z'}
                }
            }
        ]
        result = analyzer.analyze_commit_frequency(commits)

        assert len(result) == 1
        assert '2024-01-01' in result
        assert result['2024-01-01'] == 1

    def test_analyze_multiple_commits_same_day(self):
        """Test analyzing multiple commits on same day"""
        analyzer = GitHubCommitAnalyzer()
        commits = [
            {'commit': {'author': {'date': '2024-01-01T10:00:00Z'}}},
            {'commit': {'author': {'date': '2024-01-01T12:00:00Z'}}},
            {'commit': {'author': {'date': '2024-01-01T14:00:00Z'}}},
        ]
        result = analyzer.analyze_commit_frequency(commits)

        assert len(result) == 1
        assert result['2024-01-01'] == 3

    def test_analyze_multiple_commits_different_days(self):
        """Test analyzing commits across multiple days"""
        analyzer = GitHubCommitAnalyzer()
        commits = [
            {'commit': {'author': {'date': '2024-01-01T12:00:00Z'}}},
            {'commit': {'author': {'date': '2024-01-02T12:00:00Z'}}},
            {'commit': {'author': {'date': '2024-01-03T12:00:00Z'}}},
        ]
        result = analyzer.analyze_commit_frequency(commits)

        assert len(result) == 3
        assert result['2024-01-01'] == 1
        assert result['2024-01-02'] == 1
        assert result['2024-01-03'] == 1

    def test_analyze_commit_missing_date(self):
        """Test handling commits with missing date field"""
        analyzer = GitHubCommitAnalyzer()
        commits = [
            {'commit': {'author': {'date': '2024-01-01T12:00:00Z'}}},
            {'commit': {'author': {}}},  # Missing date
            {'commit': {}},  # Missing author
            {},  # Missing commit
        ]
        result = analyzer.analyze_commit_frequency(commits)

        assert len(result) == 1
        assert result['2024-01-01'] == 1

    def test_analyze_commit_returns_sorted_dict(self):
        """Test that result is sorted by date"""
        analyzer = GitHubCommitAnalyzer()
        commits = [
            {'commit': {'author': {'date': '2024-01-03T12:00:00Z'}}},
            {'commit': {'author': {'date': '2024-01-01T12:00:00Z'}}},
            {'commit': {'author': {'date': '2024-01-02T12:00:00Z'}}},
        ]
        result = analyzer.analyze_commit_frequency(commits)

        keys = list(result.keys())
        assert keys == ['2024-01-01', '2024-01-02', '2024-01-03']

    def test_analyze_commit_various_date_formats(self):
        """Test handling different time values in same day"""
        analyzer = GitHubCommitAnalyzer()
        commits = [
            {'commit': {'author': {'date': '2024-01-01T00:00:00Z'}}},
            {'commit': {'author': {'date': '2024-01-01T23:59:59Z'}}},
            {'commit': {'author': {'date': '2024-01-01T12:30:45Z'}}},
        ]
        result = analyzer.analyze_commit_frequency(commits)

        assert len(result) == 1
        assert result['2024-01-01'] == 3


class TestPlotCommitFrequency:
    """Test cases for plot_commit_frequency method"""

    @patch('test.plt.savefig')
    @patch('test.plt.show')
    def test_plot_with_save_path(self, mock_show, mock_savefig):
        """Test plotting with save path"""
        analyzer = GitHubCommitAnalyzer()
        daily_commits = {
            '2024-01-01': 5,
            '2024-01-02': 10,
            '2024-01-03': 15
        }

        result = analyzer.plot_commit_frequency(
            daily_commits,
            'owner',
            'repo',
            save_path='/path/to/save.png'
        )

        assert result == daily_commits
        mock_savefig.assert_called_once()
        mock_show.assert_not_called()

    @patch('test.plt.savefig')
    @patch('test.plt.show')
    def test_plot_without_save_path(self, mock_show, mock_savefig):
        """Test plotting without save path (shows plot)"""
        analyzer = GitHubCommitAnalyzer()
        daily_commits = {
            '2024-01-01': 5,
            '2024-01-02': 10
        }

        result = analyzer.plot_commit_frequency(
            daily_commits,
            'owner',
            'repo'
        )

        assert result == daily_commits
        mock_show.assert_called_once()
        mock_savefig.assert_not_called()

    def test_plot_empty_commits(self):
        """Test plotting with empty commits dict"""
        analyzer = GitHubCommitAnalyzer()
        result = analyzer.plot_commit_frequency({}, 'owner', 'repo')

        assert result == {}

    @patch('test.plt.savefig')
    @patch('test.plt.show')
    def test_plot_single_day(self, mock_show, mock_savefig):
        """Test plotting with single day of commits"""
        analyzer = GitHubCommitAnalyzer()
        daily_commits = {'2024-01-01': 5}

        result = analyzer.plot_commit_frequency(
            daily_commits,
            'owner',
            'repo'
        )

        assert result == daily_commits

    @patch('test.plt.savefig')
    @patch('test.plt.show')
    def test_plot_with_zero_commits(self, mock_show, mock_savefig):
        """Test plotting with zero commits day"""
        analyzer = GitHubCommitAnalyzer()
        daily_commits = {'2024-01-01': 0}

        result = analyzer.plot_commit_frequency(
            daily_commits,
            'owner',
            'repo'
        )

        assert result == daily_commits


class TestAnalyzeRepo:
    """Test cases for analyze_repo method"""

    @patch('test.plt.show')
    @patch.object(GitHubCommitAnalyzer, 'plot_commit_frequency')
    @patch.object(GitHubCommitAnalyzer, 'analyze_commit_frequency')
    @patch.object(GitHubCommitAnalyzer, 'get_commits')
    @patch.object(GitHubCommitAnalyzer, 'parse_github_url')
    def test_analyze_repo_success(self, mock_parse, mock_get, mock_analyze,
                                   mock_plot, mock_show):
        """Test successful repo analysis"""
        mock_parse.return_value = ('owner', 'repo')
        mock_get.return_value = [
            {'commit': {'author': {'date': '2024-01-01T12:00:00Z'}}}
        ]
        mock_analyze.return_value = {'2024-01-01': 1}
        mock_plot.return_value = {'2024-01-01': 1}

        analyzer = GitHubCommitAnalyzer()
        result = analyzer.analyze_repo('https://github.com/owner/repo')

        assert result == {'2024-01-01': 1}
        mock_parse.assert_called_once()
        mock_get.assert_called_once_with('owner', 'repo')
        mock_analyze.assert_called_once()
        mock_plot.assert_called_once()

    @patch.object(GitHubCommitAnalyzer, 'get_commits')
    @patch.object(GitHubCommitAnalyzer, 'parse_github_url')
    def test_analyze_repo_no_commits(self, mock_parse, mock_get):
        """Test repo analysis with no commits found"""
        mock_parse.return_value = ('owner', 'repo')
        mock_get.return_value = []

        analyzer = GitHubCommitAnalyzer()
        result = analyzer.analyze_repo('https://github.com/owner/repo')

        assert result is None

    @patch.object(GitHubCommitAnalyzer, 'parse_github_url')
    def test_analyze_repo_invalid_url(self, mock_parse):
        """Test repo analysis with invalid URL"""
        mock_parse.side_effect = ValueError("Cannot parse GitHub URL")

        analyzer = GitHubCommitAnalyzer()
        result = analyzer.analyze_repo('invalid-url')

        assert result is None

    @patch('test.plt.savefig')
    @patch.object(GitHubCommitAnalyzer, 'plot_commit_frequency')
    @patch.object(GitHubCommitAnalyzer, 'analyze_commit_frequency')
    @patch.object(GitHubCommitAnalyzer, 'get_commits')
    @patch.object(GitHubCommitAnalyzer, 'parse_github_url')
    def test_analyze_repo_with_save_path(self, mock_parse, mock_get, mock_analyze,
                                          mock_plot, mock_savefig):
        """Test repo analysis with save path"""
        mock_parse.return_value = ('owner', 'repo')
        mock_get.return_value = [
            {'commit': {'author': {'date': '2024-01-01T12:00:00Z'}}}
        ]
        mock_analyze.return_value = {'2024-01-01': 1}
        mock_plot.return_value = {'2024-01-01': 1}

        analyzer = GitHubCommitAnalyzer()
        result = analyzer.analyze_repo(
            'https://github.com/owner/repo',
            save_path='/path/to/save.png'
        )

        assert result == {'2024-01-01': 1}
        mock_plot.assert_called_once()
        call_args = mock_plot.call_args
        assert call_args[0][3] == '/path/to/save.png'

    @patch.object(GitHubCommitAnalyzer, 'parse_github_url')
    def test_analyze_repo_exception_handling(self, mock_parse):
        """Test repo analysis handles exceptions gracefully"""
        mock_parse.side_effect = Exception("Unexpected error")

        analyzer = GitHubCommitAnalyzer()
        result = analyzer.analyze_repo('https://github.com/owner/repo')

        assert result is None


class TestIntegration:
    """Integration tests for complete workflows"""

    @patch('test.plt.show')
    @patch('test.plt.savefig')
    @patch('test.requests.get')
    def test_full_analysis_workflow(self, mock_get, mock_savefig, mock_show):
        """Test complete analysis workflow from URL to plot"""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = [
            {'commit': {'author': {'date': '2024-01-01T10:00:00Z'}}},
            {'commit': {'author': {'date': '2024-01-01T14:00:00Z'}}},
            {'commit': {'author': {'date': '2024-01-02T12:00:00Z'}}},
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        analyzer = GitHubCommitAnalyzer(github_token="test_token")
        result = analyzer.analyze_repo(
            'https://github.com/owner/repo',
            save_path='/test/path.png'
        )

        assert result is not None
        assert '2024-01-01' in result
        assert '2024-01-02' in result
        assert result['2024-01-01'] == 2
        assert result['2024-01-02'] == 1
