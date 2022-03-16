#
# Copyright (c) 2021 Cisco Systems, Inc and its affiliates
# All rights reserved
#
from flask_restx import Api
from flask import Blueprint, render_template, json, jsonify, Flask


class Sso:
    def __init__(self,
                 base_url="http://localhost:9103/idm",
                 token_path="/v2/token",
                 authorize_path="/v2/authorize",
                 client_id="",
                 client_secret=""):
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
    def __init__(self,
                 root_path: str,
                 ui_path="/swagger",
                 resource_path="/swagger-resources",
                 api_path="/apidocs.json",
                 spec_version="3.0.0",
                 security=Security(False)):

        self.root_path = root_path
        self.ui_path = ui_path
        self.resource_path = resource_path
        self.api_path = api_path
        self.spec_version = spec_version
        self.security = security


class MSXSwaggerConfig:
    def __init__(self,
                 app: Flask,
                 documentation_config: DocumentationConfig,
                 swagger_resource=None):

        blueprint = Blueprint(
            name='swagger',
            import_name=__name__,
            url_prefix=documentation_config.root_path,
            template_folder='templates',
            static_folder='static')
        self.api = Api(blueprint)

        @blueprint.route(documentation_config.ui_path)
        def swagger_ui():
            config = documentation_config
            template = "secure.html" if config.security.enabled else "insecure.html",
            swagger_json = config.root_path + config.resource_path + config.api_path
            return render_template(template, swagger_json=swagger_json), 200

        @blueprint.route(documentation_config.resource_path + documentation_config.api_path)
        def swagger_resource_json():
            if swagger_resource:
                with app.open_resource(swagger_resource, "r") as file:
                    contents = file.read()
            else:
                contents = str(json.dumps(self.api.__schema__))
            return contents, 200

        @blueprint.route("/swagger-sso-redirect.html")
        def swagger_sso_redirect_html():
            return render_template('swagger-sso-redirect.html'), 200

        @blueprint.route(documentation_config.resource_path)
        def swagger_resources_configuration():
            return jsonify([{
                "name": "platform",
                "location": documentation_config.resource_path + documentation_config.api_path,
                "url": documentation_config.resource_path + documentation_config.api_path,
                "swaggerVersion": documentation_config.spec_version,
            }])

        @blueprint.route(documentation_config.resource_path + "/configuration/ui")
        def swagger_resources_configuration_ui():
            return jsonify({
                       "deepLinking": True,
                       "displayOperationId": False,
                       "defaultModelsExpandDepth": 1,
                       "defaultModelExpandDepth": 1,
                       "defaultModelRendering": "example",
                       "displayRequestDuration": False,
                       "docExpansion": "none",
                       "filter": False,
                       "operationsSorter": "alpha",
                       "showExtensions": False,
                       "showCommonExtensions": False,
                       "tagsSorter": "alpha",
                       "validatorUrl": "",
                       "supportedSubmitMethods": [
                           "get",
                           "put",
                           "post",
                           "delete",
                           "options",
                           "head",
                           "patch",
                           "trace"
                       ],
                       "swaggerBaseUiUrl": ""
                   })

        @blueprint.route(documentation_config.resource_path + "/configuration/security")
        def swagger_resources_configuration_security():
            return jsonify({})

        @blueprint.route(documentation_config.resource_path + "/configuration/security/sso")
        def swagger_resources_configuration_security_sso():
            sso = documentation_config.security.sso
            return jsonify({
                "authorizeUrl": sso.authorize_path,
                "clientId": sso.client_id,
                "tokenUrl": sso.token_path,
                "clientSecret": sso.client_secret if sso.client_secret else "",
            })
