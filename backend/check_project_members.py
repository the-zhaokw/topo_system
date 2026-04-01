from enhanced_app import db, Project, User, ProjectMember
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./instance/enhanced_bug_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # 检查项目成员关系
    project_members = ProjectMember.query.all()
    print(f'项目成员关系数量: {len(project_members)}')
    
    if len(project_members) == 0:
        print('数据库中暂无项目成员关系，需要创建一些成员关系')
    else:
        for pm in project_members:
            project = Project.query.get(pm.project_id)
            user = User.query.get(pm.user_id)
            print(f'项目: {project.name if project else "未知"}, 成员: {user.username if user else "未知"}, 角色: {pm.role}')
    
    # 检查所有用户
    users = User.query.all()
    print(f'\n所有用户:')
    for user in users:
        print(f'用户ID: {user.id}, 用户名: {user.username}, 角色: {user.role}')
    
    # 检查所有项目
    projects = Project.query.all()
    print(f'\n所有项目:')
    for project in projects:
        print(f'项目ID: {project.id}, 名称: {project.name}, 负责人ID: {project.owner_id}')