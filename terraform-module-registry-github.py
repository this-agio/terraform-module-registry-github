#!/usr/bin/env python

import flask
import re
import sys

from configuration import read_configuration
from github_client import matching_versions

modules = read_configuration(sys.argv[1])

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
    versions = matching_versions(module['repository'], re.compile(versions_expression))
    return {
        'modules': [{
            'versions': [{'version': v} for v in versions]
        }]
    }

from gunicorn_application import GunicornApplication
GunicornApplication(app, {
    'bind': '0.0.0.0:443',
    'certfile': sys.argv[2],
    'keyfile': sys.argv[3],
}).run()
