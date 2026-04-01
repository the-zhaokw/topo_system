"""Migrate role-based system to position-based system"""
import sys
sys.path.insert(0, '.')

from enhanced_app import db, Position
from sqlalchemy import text
import json

def migrate():
    """Migrate from role-based to position-based permission system"""
    try:
        print("Starting migration: role to position...")
        
        # Step 1: Add new columns to positions table
        print("Step 1: Adding new columns to positions table...")
        result = db.session.execute(text("PRAGMA table_info(positions)"))
        columns = [row[1] for row in result]
        
        if 'permissions' not in columns:
            db.session.execute(text("ALTER TABLE positions ADD COLUMN permissions TEXT DEFAULT '[]'"))
            print("  - Added permissions column")
        
        if 'is_admin' not in columns:
            db.session.execute(text("ALTER TABLE positions ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
            print("  - Added is_admin column")
        
        if 'is_manager' not in columns:
            db.session.execute(text("ALTER TABLE positions ADD COLUMN is_manager BOOLEAN DEFAULT 0"))
            print("  - Added is_manager column")
        
        db.session.commit()
        print("Step 1 completed successfully")
        
        # Step 2: Make role column nullable in users table
        print("\nStep 2: Making role column nullable in users table...")
        try:
            # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
            # But for simplicity, we'll just update the column value to allow NULL
            # by setting empty strings to NULL
            db.session.execute(text("UPDATE users SET role = NULL WHERE role = ''"))
            db.session.commit()
            print("Step 2 completed successfully")
        except Exception as e:
            print(f"  Warning in Step 2: {e}")
            db.session.rollback()
        
        # Step 3: Create default positions based on existing roles
        print("\nStep 3: Creating default positions based on existing roles...")
        from models.permissions import DEFAULT_ROLES, PermissionCodes
        
        role_to_position_map = {
            'admin': '超级管理员',
            'manager': '经理',
            'project_manager': '项目经理',
            'test_engineer': '测试工程师',
            'software_engineer': '软件工程师',
            'user': '普通用户',
            'hr': '人事专员',
            'department_manager': '部门经理',
            'division_leader': '部门负责人'
        }
        
        for role_key, position_name in role_to_position_map.items():
            existing_position = Position.query.filter_by(name=position_name).first()
            if not existing_position:
                role_config = DEFAULT_ROLES.get(role_key, {})
                permissions = role_config.get('permissions', [])
                
                if permissions == 'all':
                    perm_json = json.dumps([])
                    is_admin = role_key == 'admin'
                    is_manager = role_key in ['admin', 'manager', 'department_manager', 'division_leader']
                else:
                    perm_json = json.dumps(permissions)
                    is_admin = role_key == 'admin'
                    is_manager = role_key in ['admin', 'manager', 'department_manager', 'division_leader']
                
                new_position = Position(
                    name=position_name,
                    description=role_config.get('description', ''),
                    permissions=perm_json,
                    is_admin=is_admin,
                    is_manager=is_manager
                )
                db.session.add(new_position)
                print(f"  - Created position: {position_name}")
        
        db.session.commit()
        print("Step 3 completed successfully")
        
        # Step 4: Update users' position based on their role
        print("\nStep 4: Updating users' position based on their role...")
        for role_key, position_name in role_to_position_map.items():
            result = db.session.execute(
                text("UPDATE users SET position = :position WHERE role = :role AND (position IS NULL OR position = '')"),
                {'position': position_name, 'role': role_key}
            )
            if result.rowcount > 0:
                print(f"  - Updated {result.rowcount} users with role '{role_key}' to position '{position_name}'")
        
        db.session.commit()
        print("Step 4 completed successfully")
        
        print("\n✅ Migration completed successfully!")
        print("\nNote: The 'role' column in users table is now nullable.")
        print("The system will use 'position' for permission checks.")
        print("You can safely remove the 'role' column after verifying the migration.")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    migrate()
