#!/usr/bin/env python

import os
import sys

if not 'GITHUB_TOKEN' in os.environ:
    print('Environment variable GITHUB_TOKEN needs to contain a GitHub token.', file=sys.stderr)
    exit(1)

import yaml

config = yaml.load(open(sys.argv[1], 'r'), Loader=yaml.FullLoader)
modules = {}
for module in config['modules']:
    namespace = modules.setdefault(module['namespace'], {})
    name = namespace.setdefault(module['name'], {})
    system = name.setdefault(module['system'], module)
print(modules)

from github import Github
from github import Auth

auth = Auth.Token(os.environ['GITHUB_TOKEN'])
g = Github(auth=auth)

import flask

app = flask.Flask(__name__)

from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)


@app.route('/')
@metrics.do_not_track()
def index():
    return 'We\'re up! 👍'


@app.route('/.well-known/terraform.json')
@metrics.counter('service_discovery', 'Number of service discovery invocations')
def terraform_json():
    return {
        'modules.v1': '/modules/',
    }


@app.route('/modules/<namespace>/<name>/<system>/<version>/download')
@metrics.counter('downloads', 'Number of downloads',
                 labels={'namespace': lambda: flask.request.view_args['namespace'],
                         'name': lambda: flask.request.view_args['name'],
                         'system': lambda: flask.request.view_args['system'],
                         'version': lambda: flask.request.view_args['version'], })
def download(namespace, name, system, version):
    module = modules[namespace][name][system]
    resp = flask.Response()
    resp.status = 204
    resp.headers[
        'X-Terraform-Get'] = f'https://github.com/{module['repository']}/archive/refs/tags/{module['versions'].format(semver=version)}.tar.gz'
    return resp


@app.route('/modules/<namespace>/<name>/<system>/versions')
@metrics.counter('versions', 'Number of requests of versions',
                 labels={'namespace': lambda: flask.request.view_args['namespace'],
                         'name': lambda: flask.request.view_args['name'],
                         'system': lambda: flask.request.view_args['system'], })
def versions(namespace, name, system):
    module = modules[namespace][name][system]
    versions_expression = module['versions'].format(semver='([0-9]+.[0-9]+.[0-9]+)')
    repo = g.get_repo(module['repository'])
    versions = []
    for tag in repo.get_tags():
        import re
        if re.match(re.compile(versions_expression), tag.name):
            versions.append({'version': re.match(re.compile(versions_expression), tag.name).group(1)})
    return {
        'modules': [
            {
                'versions': versions
            }
        ]
    }



app.run(
    host='0.0.0.0',
    port=443,
    ssl_context=('cert.pem', 'key.pem')
)
