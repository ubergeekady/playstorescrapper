from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask import got_request_exception
import os
import rollbar
import rollbar.contrib.flask


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'


#On Macbook export PLAYSTORESCRAPPERAPP_DATABASEAPPURL=sqlite:///site.db
dburl = os.environ.get('PLAYSTORESCRAPPERAPP_DATABASEAPPURL')
if dburl == None:
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
else:
	app.config['SQLALCHEMY_DATABASE_URI'] = dburl


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SCRAPPER_REFRESH_DAYS'] = 30
app.config['JWT_TOKEN_EXPIRY_HOURS'] = 24

db = SQLAlchemy(app)

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

from playstorescrapperapp.models import User, App, Category, CategoryMapping

#admin = Admin(app, name='Playstore Scrapper', template_mode='bootstrap3')
#admin.add_view(ModelView(User, db.session))
#admin.add_view(ModelView(App, db.session))
#admin.add_view(ModelView(Category, db.session))
#admin.add_view(ModelView(CategoryMapping, db.session))


@app.before_first_request
def init_rollbar():
    rollbar.init(
        '5c5a8e4943b44929b0eb4276192fa310',
        'playstorescrapperapp',
        root=os.path.dirname(os.path.realpath(__file__)),
        allow_logging_basic_config=False)
    got_request_exception.connect(rollbar.contrib.flask.report_exception, app)

from playstorescrapperapp import routes
