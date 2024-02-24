import os
import sys
from github import Github, Auth

if not 'GITHUB_TOKEN' in os.environ:
    print('Environment variable GITHUB_TOKEN needs to contain a GitHub token.', file=sys.stderr)
    exit(1)


github = Github(auth=(Auth.Token(os.environ['GITHUB_TOKEN'])))