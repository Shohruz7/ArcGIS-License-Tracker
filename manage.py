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
def add_indexes():
    """Add database indexes to improve query performance (safe for existing databases)."""
    from sqlalchemy import text
    with app.app_context():
        try:
            # Get the database dialect
            dialect = db.engine.dialect.name
            
            print(f"Detected database: {dialect}")
            print("Adding indexes to improve query performance...")
            
            # SQLite uses CREATE INDEX IF NOT EXISTS
            if dialect == 'sqlite':
                indexes = [
                    ("idx_server_name", "CREATE INDEX IF NOT EXISTS idx_server_name ON server(name)"),
                    ("idx_updates_server_id", "CREATE INDEX IF NOT EXISTS idx_updates_server_id ON updates(server_id)"),
                    ("idx_updates_status", "CREATE INDEX IF NOT EXISTS idx_updates_status ON updates(status)"),
                    ("idx_updates_time_start", "CREATE INDEX IF NOT EXISTS idx_updates_time_start ON updates(time_start)"),
                    ("idx_updates_time_complete", "CREATE INDEX IF NOT EXISTS idx_updates_time_complete ON updates(time_complete)"),
                    ("idx_updates_server_time", "CREATE INDEX IF NOT EXISTS idx_updates_server_time ON updates(server_id, time_start)"),
                    ("idx_product_server_id", "CREATE INDEX IF NOT EXISTS idx_product_server_id ON product(server_id)"),
                    ("idx_product_common_name", "CREATE INDEX IF NOT EXISTS idx_product_common_name ON product(common_name)"),
                    ("idx_product_internal_name", "CREATE INDEX IF NOT EXISTS idx_product_internal_name ON product(internal_name)"),
                    ("idx_product_type", "CREATE INDEX IF NOT EXISTS idx_product_type ON product(type)"),
                    ("idx_product_server_type", "CREATE INDEX IF NOT EXISTS idx_product_server_type ON product(server_id, type)"),
                    ("idx_workstation_name", "CREATE INDEX IF NOT EXISTS idx_workstation_name ON workstation(name)"),
                    ("idx_user_name", "CREATE INDEX IF NOT EXISTS idx_user_name ON user(name)"),
                    ("idx_history_user_id", "CREATE INDEX IF NOT EXISTS idx_history_user_id ON history(user_id)"),
                    ("idx_history_workstation_id", "CREATE INDEX IF NOT EXISTS idx_history_workstation_id ON history(workstation_id)"),
                    ("idx_history_product_id", "CREATE INDEX IF NOT EXISTS idx_history_product_id ON history(product_id)"),
                    ("idx_history_update_id", "CREATE INDEX IF NOT EXISTS idx_history_update_id ON history(update_id)"),
                    ("idx_history_time_out", "CREATE INDEX IF NOT EXISTS idx_history_time_out ON history(time_out)"),
                    ("idx_history_time_in", "CREATE INDEX IF NOT EXISTS idx_history_time_in ON history(time_in)"),
                    ("idx_history_user_timein", "CREATE INDEX IF NOT EXISTS idx_history_user_timein ON history(user_id, time_in)"),
                    ("idx_history_product_timein", "CREATE INDEX IF NOT EXISTS idx_history_product_timein ON history(product_id, time_in)"),
                    ("idx_history_workstation_timein", "CREATE INDEX IF NOT EXISTS idx_history_workstation_timein ON history(workstation_id, time_in)"),
                ]
            else:
                # SQL Server, PostgreSQL, MySQL use IF NOT EXISTS or similar
                indexes = [
                    ("idx_server_name", f"CREATE INDEX idx_server_name ON server(name)"),
                    ("idx_updates_server_id", f"CREATE INDEX idx_updates_server_id ON updates(server_id)"),
                    ("idx_updates_status", f"CREATE INDEX idx_updates_status ON updates(status)"),
                    ("idx_updates_time_start", f"CREATE INDEX idx_updates_time_start ON updates(time_start)"),
                    ("idx_updates_time_complete", f"CREATE INDEX idx_updates_time_complete ON updates(time_complete)"),
                    ("idx_updates_server_time", f"CREATE INDEX idx_updates_server_time ON updates(server_id, time_start)"),
                    ("idx_product_server_id", f"CREATE INDEX idx_product_server_id ON product(server_id)"),
                    ("idx_product_common_name", f"CREATE INDEX idx_product_common_name ON product(common_name)"),
                    ("idx_product_internal_name", f"CREATE INDEX idx_product_internal_name ON product(internal_name)"),
                    ("idx_product_type", f"CREATE INDEX idx_product_type ON product(type)"),
                    ("idx_product_server_type", f"CREATE INDEX idx_product_server_type ON product(server_id, type)"),
                    ("idx_workstation_name", f"CREATE INDEX idx_workstation_name ON workstation(name)"),
                    ("idx_user_name", f"CREATE INDEX idx_user_name ON [user](name)" if dialect == 'mssql' else f"CREATE INDEX idx_user_name ON user(name)"),
                    ("idx_history_user_id", f"CREATE INDEX idx_history_user_id ON history(user_id)"),
                    ("idx_history_workstation_id", f"CREATE INDEX idx_history_workstation_id ON history(workstation_id)"),
                    ("idx_history_product_id", f"CREATE INDEX idx_history_product_id ON history(product_id)"),
                    ("idx_history_update_id", f"CREATE INDEX idx_history_update_id ON history(update_id)"),
                    ("idx_history_time_out", f"CREATE INDEX idx_history_time_out ON history(time_out)"),
                    ("idx_history_time_in", f"CREATE INDEX idx_history_time_in ON history(time_in)"),
                    ("idx_history_user_timein", f"CREATE INDEX idx_history_user_timein ON history(user_id, time_in)"),
                    ("idx_history_product_timein", f"CREATE INDEX idx_history_product_timein ON history(product_id, time_in)"),
                    ("idx_history_workstation_timein", f"CREATE INDEX idx_history_workstation_timein ON history(workstation_id, time_in)"),
                ]
            
            created = 0
            skipped = 0
            for idx_name, sql in indexes:
                try:
                    db.session.execute(text(sql))
                    created += 1
                    print(f"  ✓ Created index: {idx_name}")
                except Exception as e:
                    # Index might already exist
                    if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                        skipped += 1
                        print(f"  - Index already exists: {idx_name}")
                    else:
                        print(f"  ✗ Error creating {idx_name}: {str(e)}")
            
            db.session.commit()
            print(f"\n✓ Index creation complete!")
            print(f"  Created: {created} indexes")
            if skipped > 0:
                print(f"  Skipped (already exist): {skipped} indexes")
            print("\nNote: Indexes will be automatically created when using 'recreate_db' command.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding indexes: {str(e)}")
            print("You may need to add indexes manually or recreate the database.")


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
@click.option('--no-scheduler', is_flag=True, help='Disable automatic scheduler startup')
def runserver(host, port, no_scheduler):
    """Run the development server."""
    if not no_scheduler:
        # Start the scheduler automatically when running the server
        from app.scheduler_jobs import start_scheduler
        with app.app_context():
            start_scheduler()
            print("✓ Background scheduler started (license reading will run automatically)")
    
    print(f"Starting server on http://{host}:{port}")
    app.run(host=host, port=port, debug=True, threaded=True)


@cli.command()
def scheduler_start():
    """Start the background scheduler for automated license reading."""
    from app.scheduler_jobs import start_scheduler, get_scheduler_status
    with app.app_context():
        start_scheduler()
        status = get_scheduler_status()
        print("✓ Scheduler started")
        if status['job_exists']:
            print(f"  Next run: {status['next_run_time']}")
            print(f"  Interval: {status['interval_minutes']} minutes")


@cli.command()
def scheduler_stop():
    """Stop the background scheduler."""
    from app.scheduler_jobs import stop_scheduler
    with app.app_context():
        stop_scheduler()
        print("✓ Scheduler stopped")


@cli.command()
def scheduler_status():
    """Show the current status of the background scheduler."""
    from app.scheduler_jobs import get_scheduler_status
    with app.app_context():
        status = get_scheduler_status()
        print("Scheduler Status:")
        print(f"  Running: {'Yes' if status['running'] else 'No'}")
        print(f"  Job exists: {'Yes' if status['job_exists'] else 'No'}")
        if status['next_run_time']:
            print(f"  Next run: {status['next_run_time']}")
        if status['interval_minutes']:
            print(f"  Interval: {status['interval_minutes']} minutes")
        else:
            print("  Interval: Not configured")


# Flask-Migrate commands (delegated to flask db commands)
# Users can use: flask db init, flask db migrate, flask db upgrade, flask db downgrade
# These are available via Flask CLI, not through manage.py


if __name__ == '__main__':
    cli()
