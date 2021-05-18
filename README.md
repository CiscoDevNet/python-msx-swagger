## msxswagger
This module adds swagger ui to flask applications, based on annotated routes.

### Prerequisites:
- python3
- pip3
- Flask

### Installation:
```bash
pip3 install msxswagger
```
### Usage - Default MSX Configuration: 
Replace sampleservice with whichever root route you prefer; can be '/'

``` python
from flask import Flask, Blueprint, render_template
from msxswagger import MSXSwaggerDefaultConfig
app = Flask(__name__)
msx_swagger = MSXSwaggerDefaultConfig(app, '/sampleservice')

app.register_blueprint(msx_swagger.api.blueprint)
app.run(host='127.0.0.1', port=8081)
```

The snippet above will display the swagger ui at the following route: 
>127.0.0.1:8081/sampleservice/swaggerui

An example of adding a new route:
```python
@msx_swagger.api.route('/')
class MainClass(msx_swagger.resource):
    def get(self):
        return {'Hello': 'World'}
```
Please note how the returned object msx_swagger's resource attribute is passed in as the base class to your route's class.
The class must be toggled with the msx_swagger.api object as well.
Your new route can be accessed as:
> 127.0.0.1:8081/sampleservice/

Since swagger typically only displays api calls that return data only, here is an example of how to have separate APIs that return UI objects. 
This will not be displayed in swagger.

First, you create a new flask blueprint
```python
ui = Blueprint('root', __name__, url_prefix='/ui')
```
Then create your ui route:
```python
@ui.route('/')
def homepage():
    return render_template('index.html', title="Hello World"), 200
```
Of course, this assumes there is an index.html file in the templates directory of your flask project.
Finally, be sure to register your blueprints with your flask application.
```python
app.register_blueprint(ui)
app.register_blueprint(msx_swagger.api.blueprint)
app.run(host='127.0.0.1', port=8081)
```

### Usage - Additional Configuration

#### Modify swagger name and description
```python
from msxswagger import MSXSwaggerConfig, AppInfo
msx_swagger = MSXSwaggerConfig(app, AppInfo(name='My Sample Service', description='The Sample Service to demonstrate e2e', version=1.0))
```
The parameters above will display on the swagger page

#### Modify the swagger url 
To modify the url of the swagger ui, simply set swagger_ui below to be the url you want it to be displayed on.
```python
from msxswagger import MSXSwaggerConfig, Security, DocumentationConfig
documentation_config = DocumentationConfig(root_path='/', swagger_json_path='/swagger.json', swagger_ui='/mylocation/swaggerui', spec_version='3.0.0', 
security=Security(False))
msx_swagger = MSXSwaggerConfig(app, documentation_config=documentation_config)
```
Other DocumentationConfig properties:
- root_path : This is the root path from which all other routes will be appended to
- swagger_json_path : This is the location of where your swagger.json file is returned from. The default is /root_path/swagger.json.
If you want swagger ui to display swagger json from different route, specify that route here, and be sure to set disable_swagger_json_generation to True
in MSXSwaggerConfig
- swagger_ui :  This is the url you want your swagger ui to be displayed at 
- spec_version : This is the version of open api that is used for the swagger.json file; default is 3.0.0
- security : This enables you to configure the MSX SSO Client with your application. See Security / Authorization section for details

MSXSwaggerConfig properties:
- app: this is the reference to your Flask app
- app_info: AppInfo object instance as described above
- documentation_config: DocumentationConfig as described in the above section
- disable_swagger_json_generation: This is a boolean parameter; this is in the event that you don't want swagger to display the routes based on the @msx_swagger.api routing.
Typically people do this if they want to provide their own swagger.json file. In order for swagger ui to display the desired json file; be sure to set swagger_json_path
property in DocumentationConfig to be a valid route that returns a json file format, the following being an example:
```python
        @app.route('/swagger.json')
        def swagger_json():
            content = str(json.dumps('CONTENTS_OF_YOUR_SWAGGER_FILE_HERE'))
            return Response(content,
                            mimetype='application/json',
                            headers={'Content-Disposition': 'attachment;filename=swagger.json'})
```

### Security / Authorization
##### Configuring MSX SSO with Swagger
In order to allow users to authenticate via swagger, you will need a valid SSO Client, which can be configured through settings in MSX.
By default, authorization is disabled, you can enable/configure it as follows:
```python
from msxswagger import MSXSwaggerConfig, AppInfo, DocumentationConfig, Security, Sso
sso = Sso(base_url='https://<MSX_URL>/idm', token_path='/v2/token', authorize_path='/v2/authorize')
documentation_config = DocumentationConfig(root_path='/', swagger_json_path='/swagger.json', swagger_ui='/swaggerui', spec_version='3.0.0', 
security=Security(True, sso))
msx_swagger = MSXSwaggerConfig(app, documentation_config=documentation_config)
```

Now, when you go to swagger, you'll be able to authorize in swagger, and have the token bearer be included in all api calls