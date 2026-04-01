"""Add owner_id to requirement_documents table"""
import sys
sys.path.insert(0, '.')

from enhanced_app import db
from sqlalchemy import text

def migrate():
    """Add owner_id column to requirement_documents table"""
    try:
        # Check if column exists
        result = db.session.execute(text("PRAGMA table_info(requirement_documents)"))
        columns = [row[1] for row in result]
        
        if 'owner_id' not in columns:
            db.session.execute(text("ALTER TABLE requirement_documents ADD COLUMN owner_id INTEGER REFERENCES users(id)"))
            db.session.commit()
            print("Successfully added owner_id column to requirement_documents table")
        else:
            print("owner_id column already exists in requirement_documents table")
    except Exception as e:
        db.session.rollback()
        print(f"Error migrating database: {e}")
        raise

if __name__ == '__main__':
    migrate()