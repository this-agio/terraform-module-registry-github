import os
import re
import sys
from github import Github, Auth

if not 'GITHUB_TOKEN' in os.environ:
    print('Environment variable GITHUB_TOKEN needs to contain a GitHub token.', file=sys.stderr)
    exit(1)


github = Github(auth=(Auth.Token(os.environ['GITHUB_TOKEN'])))


def matching_versions(repo, regular_expression):
    repo = github.get_repo(repo)
    versions = [re.match(regular_expression, tag.name).group(1)
                for tag in repo.get_tags()
                if re.match(regular_expression, tag.name)]
    return versions
