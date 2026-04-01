from enhanced_app import app, db, User

# 直接使用enhanced_app中的app实例

with app.app_context():
    try:
        print("检查数据库用户表...")
        
        # 查询所有用户
        users = User.query.all()
        
        print(f"找到 {len(users)} 个用户")
        
        # 显示用户信息
        for user in users:
            print(f"用户ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}, 角色: {user.role}, 活跃状态: {user.is_active}")
            
        # 检查是否有管理员用户
        admin_users = User.query.filter_by(role='admin').all()
        print(f"\n管理员用户数量: {len(admin_users)}")
        
        print("\n数据库用户表检查完成，状态正常！")
        
    except Exception as e:
        print(f"数据库检查失败: {str(e)}")