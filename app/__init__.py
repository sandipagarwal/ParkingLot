from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

parking_lot = Flask(__name__)
parking_lot.config.from_object(Config)
db = SQLAlchemy(parking_lot)
migrate = Migrate(parking_lot, db)

from app import models
