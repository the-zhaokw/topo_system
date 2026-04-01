from run_app import db, app
from enhanced_app import User, Project, ProjectMember

with app.app_context():
    # 检查项目成员关系
    try:
        # 获取admin用户
        admin_user = User.query.filter_by(username='admin').first()
        print(f'admin用户信息: ID={admin_user.id}, 用户名={admin_user.username}, 角色={admin_user.role}')
        
        # 获取所有项目
        projects = Project.query.all()
        print(f'\n项目总数: {len(projects)}')
        
        # 检查admin是否已经是所有项目的成员
        admin_project_memberships = ProjectMember.query.filter_by(user_id=admin_user.id).all()
        print(f'\nadmin参与的项目数量: {len(admin_project_memberships)}')
        
        # 确保admin添加到所有项目中作为manager角色
        added_count = 0
        updated_count = 0
        
        print('\n正在检查并更新admin用户的项目成员关系...')
        for project in projects:
            # 检查admin是否已经是该项目的成员
            existing_member = ProjectMember.query.filter_by(project_id=project.id, user_id=admin_user.id).first()
            
            if not existing_member:
                print(f'添加admin用户到项目: {project.name}，角色: manager')
                # 创建项目成员关系，设置为manager角色
                pm = ProjectMember(
                    project_id=project.id,
                    user_id=admin_user.id,
                    role='manager'
                )
                db.session.add(pm)
                added_count += 1
            elif existing_member.role != 'manager':
                print(f'更新admin在项目: {project.name}中的角色为manager')
                existing_member.role = 'manager'
                updated_count += 1
        
        # 提交所有更改
        db.session.commit()
        
        # 显示操作结果
        if added_count > 0 or updated_count > 0:
            print(f'\n操作完成:')
            print(f'- 新增项目成员关系: {added_count}个')
            print(f'- 更新角色: {updated_count}个')
        else:
            print('\nadmin已经是所有项目的manager角色成员')
        
        # 再次检查确认
        updated_project_count = ProjectMember.query.filter_by(user_id=admin_user.id).count()
        print(f'\n操作后，admin参与的项目数量: {updated_project_count}')
        if updated_project_count == len(projects):
            print('✅ 成功：admin现在参与了所有项目！')
        else:
            print(f'⚠️ 警告：admin仍未参与所有项目，差异数: {len(projects) - updated_project_count}')
            
        # 显示admin参与的项目
            print('\nadmin参与的项目:')
            for pm in admin_project_memberships:
                project = Project.query.get(pm.project_id)
                if project:
                    print(f'- 项目: {project.name}, 角色: {pm.role}')
        
        # 检查最近一个项目的所有成员
        if projects:
            print(f'\n项目 "{projects[0].name}" 的所有成员:')
            members = ProjectMember.query.filter_by(project_id=projects[0].id).all()
            for pm in members:
                user = User.query.get(pm.user_id)
                if user:
                    print(f'- 用户: {user.username}, 角色: {pm.role}')
                    
    except Exception as e:
        print(f'发生错误: {str(e)}')
        db.session.rollback()