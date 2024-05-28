from api import app,Blueprint
from .controllers.contact_us import contact_us_route
api = Blueprint('api', __name__, url_prefix='/api')
# web = Blueprint('web',__name__)

api.register_blueprint(contact_us_route)

app.register_blueprint(api)
    