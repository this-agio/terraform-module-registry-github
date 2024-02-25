#!/usr/bin/env python

import flask
import sys
from prometheus_flask_exporter import PrometheusMetrics

from configuration import config, find_module
from github_client import versions_from_tags, download_url

app = flask.Flask(__name__)

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
    module = find_module(namespace, name, system)
    if module is None:
        return flask.abort(404)
    resp = flask.Response()
    resp.status = 204
    resp.headers['X-Terraform-Get'] = download_url(module, version)
    return resp

@app.route('/modules/<namespace>/<name>/<system>/versions')
@metrics.counter('versions', 'Number of requests of versions',
                 labels={'namespace': lambda: flask.request.view_args['namespace'],
                         'name': lambda: flask.request.view_args['name'],
                         'system': lambda: flask.request.view_args['system'], })
def versions(namespace, name, system):
    module = find_module(namespace, name, system)
    if module is None:
        return flask.abort(404)
    return {
        'modules': [{
            'versions': [{'version': v} for v in versions_from_tags(module)]
        }]
    }

from gunicorn_application import GunicornApplication
GunicornApplication(app, {
    'bind': '0.0.0.0:443',
    'certfile': sys.argv[2],
    'keyfile': sys.argv[3],
}).run()
