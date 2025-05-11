from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    conn = db.engine.connect()
    try:
        result = conn.execute(text('SELECT * FROM alembic_version'))
        print('Alembic version table exists.')
        for row in result:
            print(row)
    except Exception as e:
        print('Alembic version table error:', e)
    finally:
        conn.close() 