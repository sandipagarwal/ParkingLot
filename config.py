import os


class Config(object):
    basedir = os.path.abspath(os.path.dirname(__file__))

    # SQL Alchemy settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'parking_lot.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
