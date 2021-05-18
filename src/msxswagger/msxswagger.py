#
# Copyright (c) 2021 Cisco Systems, Inc and its affiliates
# All rights reserved
#
from flask_restplus import Resource, Api
from flask import Blueprint, render_template, Response, json


class Sso:
    def __init__(self, base_url='http://localhost:9103/idm',
                 token_path='/v2/token',
                 authorize_path='/v2/authorize',
                 client_id='', client_secret=''):
        self.base_url = base_url
        self.token_path = self.base_url + token_path
        self.authorize_path = self.base_url + authorize_path
        self.client_id = client_id
        self.client_secret = client_secret


class Security:
    def __init__(self, enabled=False, sso=Sso()):
        self.enabled = enabled
        self.sso = sso


class DocumentationConfig:
    def __init__(self, root_path: str, swagger_json_path: str,
                 swagger_ui: str, spec_version, security: Security):
        self.root_path = root_path
        self.swagger_json_path = swagger_json_path  # default= swagger json
        self.swagger_ui = swagger_ui  # i.e. /swaggerui
        self.spec_version = spec_version
        self.security = security  # security class


class AppInfo:
    def __init__(self, name: str, description: str, version):
        self.name = name
        self.description = description
        self.version = version


class MSXSwaggerDefaultConfig:
    def __init__(self, app, root_path='/sampleservice'):
        self.documentation_config = DocumentationConfig(root_path, root_path + '/swagger.json',
                                                        root_path + '/swaggerui', '3.0.0', Security(False))
        self.app_info = AppInfo(name='sample', description='This is a sample service', version=1.0)

        self.api = Api(
            Blueprint('swagger', __name__, url_prefix=self.documentation_config.root_path,
                      template_folder='templates',
                      static_folder='static', static_url_path='/%s' % __name__), doc=False)
        self.resource = Resource

        @app.route(self.documentation_config.swagger_json_path)
        def swagger_json():
            content = str(json.dumps(self.api.__schema__))
            return Response(content,
                            mimetype='application/json',
                            headers={'Content-Disposition': 'attachment;filename=swagger.json'})

        @app.route(self.documentation_config.swagger_ui)  # url for swagger ui
        def swagger_ui():
            return render_template('index.html', swagger_json=self.documentation_config.swagger_json_path), 200


class MSXSwaggerConfig:
    def __init__(self, app, app_info=AppInfo('sample', 'This is a sample service', 1.0),
                 documentation_config=DocumentationConfig('', '/swagger.json', '/swaggerui', '3.0.0', Security(False)),
                 disable_swagger_json_generation=False):
        self.documentation_config = documentation_config
        self.app_info = app_info
        self.resource = Resource

        if disable_swagger_json_generation is False:
            @app.route(self.documentation_config.swagger_json_path)
            def swagger_json():
                content = str(json.dumps(self.api.__schema__))
                return Response(content,
                                mimetype='application/json',
                                headers={'Content-Disposition': 'attachment;filename=swagger.json'})

        if documentation_config.security.enabled:
            auth = {
                'oauth2': {
                    'type': 'oauth2',
                    'authorizationUrl': self.documentation_config.security.sso.authorize_path,
                    'tokenUrl': self.documentation_config.security.sso.token_path,
                    'flow': 'password',
                    'scopes': {
                        'read': 'read',
                    }
                }
            }
            self.api = Api(
                Blueprint('swagger', __name__, url_prefix=self.documentation_config.root_path,
                          template_folder='templates',
                          static_folder='static', static_url_path='/%s' % __name__), security='oauth2', authorizations=auth)
        else:
            self.api = Api(
                Blueprint('swagger', __name__, url_prefix=self.documentation_config.root_path,
                          template_folder='templates',
                          static_folder='static', static_url_path='/%s' % __name__), doc=False)

        @app.route(self.documentation_config.swagger_ui)  # url for swagger ui
        def swagger_ui():
            return render_template('index.html', swagger_json=self.documentation_config.swagger_json_path), 200
