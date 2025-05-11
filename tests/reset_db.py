from app import create_app, db

def reset_database():
    """Drop and recreate all tables"""
    app = create_app()
    with app.app_context():
        # Drop all tables
        print("Dropping all tables...")
        db.drop_all()
        
        # Recreate all tables
        print("Recreating all tables...")
        db.create_all()
        
        print("Database has been completely reset.")

if __name__ == "__main__":
    reset_database() 