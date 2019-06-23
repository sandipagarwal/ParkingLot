import click

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

parking_lot = Flask(__name__)
parking_lot.config.from_object(Config)
db = SQLAlchemy(parking_lot)
migrate = Migrate(parking_lot, db)

from app import models, utils

@parking_lot.cli.command()
@click.argument('file_path', required=False) # Input file, optional
def run_parking_lot(file_path=None):
    """
    Run the parking lot game
    """

    # TODO: This function can be better optimized

    # Read the file, if present and play the game
    if file_path:
        with open(file_path, 'rU') as input_file:
            for command_input in input_file:
                command_input = command_input.rstrip('\n').rstrip()
                exit_status_or_message = utils.process_command_input(command_input)
                if exit_status_or_message == 0: # Exit status
                    return
                else:
                    print exit_status_or_message
    else: # play the game using console input
        command_input = raw_input().rstrip()
        while 1:
            exit_status_or_message = utils.process_command_input(command_input)
            if exit_status_or_message == 0: # Exit status
                return
            else:
                print exit_status_or_message

            # Read next line
            command_input = raw_input().rstrip()
