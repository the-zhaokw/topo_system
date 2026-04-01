#!/usr/bin/env python3
"""
添加新项目脚本
添加用户指定的项目到数据库中
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_app import db, Project, User, ProjectMember
from flask import Flask
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///topo_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def add_new_projects():
    """添加新项目数据"""
    
    with app.app_context():
        # 检查现有用户
        users = User.query.all()
        print(f"现有用户数量: {len(users)}")
        
        # 创建用户映射表
        user_map = {}
        for user in users:
            user_map[user.username] = user.id
        
        # 新项目数据 - 基于用户需求
        new_projects_data = [
            {
                "name": "NMS/LCT",
                "description": "NMS/LCT 网络管理系统项目",
                "manager": "project_manager",
                "members": ["project_manager", "developer1", "developer2", "tester1"]
            },
            {
                "name": "NSN hiT 7090",
                "description": "NSN hiT 7090 项目",
                "manager": "project_manager",
                "members": ["project_manager", "developer1", "developer2", "tester1"]
            },
            {
                "name": "NSN hiT 7090 Field",
                "description": "NSN hiT 7090 Field 现场部署项目",
                "manager": "project_manager",
                "members": ["project_manager", "developer1", "developer2", "tester1"]
            },
            {
                "name": "OTN",
                "description": "OTN 光传输网络项目",
                "manager": "project_manager",
                "members": ["project_manager", "developer1", "developer2", "tester1"]
            },
            {
                "name": "PTN WB/WS",
                "description": "PTN WB/WS 分组传送网络项目",
                "manager": "project_manager",
                "members": ["project_manager", "developer1", "developer2", "tester1"]
            },
            {
                "name": "RBBN",
                "description": "RBBN 项目",
                "manager": "project_manager",
                "members": ["project_manager", "developer1", "developer2", "tester1"]
            },
            {
                "name": "RTN",
                "description": "RTN 项目",
                "manager": "project_manager",
                "members": ["project_manager", "developer1", "developer2", "tester1"]
            }
        ]
        
        created_projects = []
        
        for project_data in new_projects_data:
            # 检查项目是否已存在
            existing_project = Project.query.filter_by(name=project_data["name"]).first()
            if existing_project:
                print(f"项目 '{project_data['name']}' 已存在，跳过创建")
                created_projects.append(existing_project)
                continue
            
            # 获取项目经理ID
            manager_username = project_data["manager"]
            owner_id = user_map.get(manager_username)
            
            if not owner_id:
                # 如果经理用户不存在，使用admin作为默认负责人
                owner_id = user_map.get("admin", 1)
                print(f"警告: 用户 '{manager_username}' 不存在，使用admin作为项目负责人")
            
            # 创建项目
            project = Project(
                name=project_data["name"],
                description=project_data["description"],
                owner_id=owner_id,
                status="active"
            )
            
            db.session.add(project)
            db.session.flush()  # 获取项目ID
            
            # 添加项目成员
            members_added = set()
            
            # 添加项目经理
            if owner_id:
                member = ProjectMember(
                    project_id=project.id,
                    user_id=owner_id,
                    role="manager"
                )
                db.session.add(member)
                members_added.add(owner_id)
            
            # 添加其他成员
            for member_username in project_data["members"]:
                member_id = user_map.get(member_username)
                if member_id and member_id not in members_added:
                    member = ProjectMember(
                        project_id=project.id,
                        user_id=member_id,
                        role="member"
                    )
                    db.session.add(member)
                    members_added.add(member_id)
                elif not member_id:
                    print(f"警告: 用户 '{member_username}' 不存在，跳过添加")
            
            created_projects.append(project)
            print(f"创建项目: {project.name} (ID: {project.id})")
        
        # 提交到数据库
        db.session.commit()
        
        print(f"\n成功创建 {len(created_projects)} 个项目")
        
        # 显示创建的项目信息
        print("\n创建的项目列表:")
        for project in created_projects:
            members = ProjectMember.query.filter_by(project_id=project.id).all()
            member_names = []
            for member in members:
                user = User.query.get(member.user_id)
                if user:
                    member_names.append(user.username)
            
            print(f"- {project.name}: {', '.join(member_names)}")

if __name__ == "__main__":
    try:
        add_new_projects()
        print("\n新项目数据创建完成!")
    except Exception as e:
        print(f"创建项目数据时出错: {str(e)}")
        import traceback
        traceback.print_exc()