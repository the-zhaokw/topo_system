import sys
sys.path.append('.')
from enhanced_app import db, Bug, Project
from app import app

with app.app_context():
    # 检查bug和项目的关联关系
    bugs = Bug.query.limit(3).all()
    print('Bug数量:', len(bugs))
    
    for bug in bugs:
        print(f'Bug ID: {bug.id}, Title: {bug.title}')
        if bug.project:
            print(f'  Project ID: {bug.project.id}, Project Name: {bug.project.name}')
        else:
            print('  No project associated')
        print('---')