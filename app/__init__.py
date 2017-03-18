from sanic import Sanic
from sanic.response import text, json

from config import Config

# blueprints imports
from app.event import event
from app.person import person
from app.university import university


# Sanic Setup - Create App
def create_app():
    app = Sanic(__name__)

    app.register_blueprint(person, url_prefix='/person')
    app.register_blueprint(event, url_prefix='/event')
    app.register_blueprint(university, url_prefix='/university')


    @app.route('/', methods=['GET'])
    async def index(request):
        return text('test')

    app.run(**Config)
