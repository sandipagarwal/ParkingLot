import os


class Config(object):
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    APP_DB = 'parking_lot.db'
    TEST_DB = 'parking_lot_test.db' # TODO: Can be derived from APP_DB

    # SQL Alchemy settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(BASEDIR, APP_DB)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
