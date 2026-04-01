from enhanced_app import app, db, User, Task, Project
from sqlalchemy import text

def test_database_connection():
    """测试数据库连接和基本查询功能"""
    with app.app_context():
        try:
            # 测试数据库连接
            print("测试数据库连接...")
            result = db.session.execute(text('SELECT 1')).scalar()
            print(f"数据库连接成功: {result}")
            
            # 测试User表
            print("\n测试User表查询...")
            users = User.query.limit(5).all()
            print(f"查询到 {len(users)} 个用户")
            for user in users:
                print(f"  - 用户: {user.username}, 邮箱: {user.email}, 角色: {user.role}")
            
            # 测试Task表
            print("\n测试Task表查询...")
            tasks = Task.query.limit(5).all()
            print(f"查询到 {len(tasks)} 个任务")
            for task in tasks:
                print(f"  - 任务: {task.title}, 创建者ID: {task.creator_id}")
            
            # 测试Project表
            print("\n测试Project表查询...")
            projects = Project.query.limit(5).all()
            print(f"查询到 {len(projects)} 个项目")
            for project in projects:
                # 打印项目的可用属性
                print(f"  - 项目: {project.name}")
                # 尝试获取并打印其他属性
                project_attrs = []
                for attr in ['id', 'description', 'created_at', 'updated_at']:
                    if hasattr(project, attr):
                        value = getattr(project, attr)
                        project_attrs.append(f"{attr}: {value}")
                if project_attrs:
                    print(f"    项目属性: {', '.join(project_attrs)}")
            
            print("\n数据库连接和模型测试成功!")
            return True
        except Exception as e:
            print(f"\n数据库测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    test_database_connection()