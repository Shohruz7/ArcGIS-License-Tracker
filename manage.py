import unittest
import click
from flask import Flask
from app import app, db
from app.fake_populate import populate


@click.group()
def cli():
    """Management commands for the Flask application."""
    pass


@cli.command()
def recreate_db():
    """Create the SQL database."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.commit()
        print("recreated the database")


@cli.command()
def fake_populate():
    """Load dummy data into db"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.commit()
        populate()
        print("populated database with dummy data")


@cli.command()
def test():
    """Run unit tests."""
    tests = unittest.TestLoader().discover('tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@cli.command()
def read_once():
    """A one-time read from the license server."""
    from app.read_licenses import read
    with app.app_context():
        read()
        print('Read completed.')


@cli.command()
@click.option('--host', default='127.0.0.1', help='The host to bind to')
@click.option('--port', default=5001, help='The port to bind to')
def runserver(host, port):
    """Run the development server."""
    print(f"Starting server on http://{host}:{port}")
    app.run(host=host, port=port, debug=True, threaded=True)


if __name__ == '__main__':
    cli()
