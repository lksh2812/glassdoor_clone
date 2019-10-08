from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment
from celery import Celery
# from elasticsearch import Elasticsearch

app = Flask(__name__)
app.app_context().push()
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
loginmanager = LoginManager(app)
loginmanager.login_view = 'login'
moment = Moment(app)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
celery.conf.update(app.config)
# app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
#     if app.config['ELASTICSEARCH_URL'] else None


from app import routes, models, errors
