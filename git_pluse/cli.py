"""
Command line interface for git-pluse
"""

import argparse
import sys
import os


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='GitHub commit analyzer - analyze and visualize commit frequency',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  git-pluse https://github.com/owner/repo
      Generate JSON output with commit records

  git-pluse https://github.com/owner/repo show
      Generate both JSON and PNG chart
        """
    )

    parser.add_argument(
        'url',
        help='GitHub repository URL'
    )

    parser.add_argument(
        'action',
        nargs='?',
        choices=['show'],
        help='Action: "show" to generate PNG chart in addition to JSON'
    )

    parser.add_argument(
        '-o', '--output',
        default='.',
        help='Output directory (default: current directory)'
    )

    parser.add_argument(
        '--token',
        help='GitHub personal access token (optional, increases API rate limit)'
    )

    args = parser.parse_args()

    # Ensure output directory exists
    output_dir = args.output
    if output_dir != '.' and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Import and use analyzer
    from .analyzer import GitHubCommitAnalyzer

    analyzer = GitHubCommitAnalyzer(github_token=args.token)

    show_chart = args.action == 'show'
    result = analyzer.analyze_repo(args.url, output_dir=output_dir, show_chart=show_chart)

    if result:
        print(f"\nAnalysis completed! Total {len(result)} days with commit records")
        sys.exit(0)
    else:
        print("\nAnalysis failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
