import os
from app.main import create_app
from flask.cli import FlaskGroup

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
cli = FlaskGroup(app)

if __name__ == '__main__':
    cli()
