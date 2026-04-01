from enhanced_app import app, db

with app.app_context():
    # 删除所有表
    db.drop_all()
    print("所有表已删除")
    
    # 重新创建所有表
    db.create_all()
    print("所有表已重新创建")
    
    print("数据库表结构更新完成")