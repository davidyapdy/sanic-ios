from sanic import Sanic
from sanic.response import text, json

# blueprints imports
from app.event import event
from app.person import person
from app.university import university

universal = os.environ['UNIVERSAL_API']
account_sid = "wow"
auth_token = "dankmemes"

# Sanic Setup - Create App
async def create_app(config=config.base_config):
    app = Sanic(__name__)
    app.config.from_object(config)

    register_blueprint(app)

    @app.route('/', methods=['GET'])
    def index():
        return text('Hello world!, Youre in the wrong spot')

# Register Blueprint
async def register_blueprint(app):
    app.register_blueprint(person, url_prefix='/person')
    app.register_blueprint(event, url_prefix='/event')
    app.register_blueprint(university, url_prefix='/university')


