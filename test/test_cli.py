"""
Unit tests for CLI
"""

import pytest
from unittest.mock import Mock, patch
import sys

sys.path.insert(0, '/workspace')


class TestCLI:
    """Test cases for CLI"""

    @patch('git_pluse.cli.GitHubCommitAnalyzer')
    def test_cli_basic_call(self, mock_analyzer):
        """Test basic CLI call"""
        mock_instance = Mock()
        mock_instance.analyze_repo.return_value = {'2024-01-01': 5}
        mock_analyzer.return_value = mock_instance

        from git_pluse.cli import main
        import sys

        test_args = ['git-pluse', 'https://github.com/owner/repo']
        with patch.object(sys, 'argv', test_args):
            try:
                main()
            except SystemExit as e:
                assert e.code == 0

        mock_instance.analyze_repo.assert_called_once()
        call_args = mock_instance.analyze_repo.call_args
        assert call_args[0][0] == 'https://github.com/owner/repo'
        assert call_args[1]['show_chart'] is False

    @patch('git_pluse.cli.GitHubCommitAnalyzer')
    def test_cli_with_show(self, mock_analyzer):
        """Test CLI with show action"""
        mock_instance = Mock()
        mock_instance.analyze_repo.return_value = {'2024-01-01': 5}
        mock_analyzer.return_value = mock_instance

        from git_pluse.cli import main
        import sys

        test_args = ['git-pluse', 'https://github.com/owner/repo', 'show']
        with patch.object(sys, 'argv', test_args):
            try:
                main()
            except SystemExit as e:
                assert e.code == 0

        call_args = mock_instance.analyze_repo.call_args
        assert call_args[1]['show_chart'] is True

    @patch('git_pluse.cli.GitHubCommitAnalyzer')
    def test_cli_with_token(self, mock_analyzer):
        """Test CLI with token"""
        mock_instance = Mock()
        mock_instance.analyze_repo.return_value = {'2024-01-01': 5}
        mock_analyzer.return_value = mock_instance

        from git_pluse.cli import main
        import sys

        test_args = ['git-pluse', 'https://github.com/owner/repo', '--token', 'ghp_test']
        with patch.object(sys, 'argv', test_args):
            try:
                main()
            except SystemExit as e:
                assert e.code == 0

        mock_analyzer.assert_called_once_with(github_token='ghp_test')
