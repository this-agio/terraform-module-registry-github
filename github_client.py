import os
import re
import sys
from github import Github, Auth

from configuration import config

if not 'GITHUB_TOKEN' in os.environ:
    print('Environment variable GITHUB_TOKEN needs to contain a GitHub token.', file=sys.stderr)
    exit(1)

github = Github(auth=(Auth.Token(os.environ['GITHUB_TOKEN'])))


def versions_from_tags(module):
    repo = module['repository']
    version_re = re.compile(module['versions'].format(semver=config['semver_regexp']))
    repo = github.get_repo(repo)
    versions = [re.match(version_re, tag.name).group('version')
                for tag in repo.get_tags()
                if re.match(version_re, tag.name)]
    return versions

def download_url(module, version):
    return f'https://github.com/{module['repository']}/archive/refs/tags/{module['versions'].format(semver=version)}.tar.gz'