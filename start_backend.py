#!/usr/bin/env python
"""启动后端服务的脚本"""
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# 导入enhanced_app模块
import enhanced_app

# 注册API蓝图
enhanced_app.register_api_blueprints()

# 初始化扩展和数据库
enhanced_app.init_extensions(enhanced_app.app)
enhanced_app.init_db()

# 启动应用
if __name__ == '__main__':
    print("Starting backend server on http://localhost:5000")
    enhanced_app.app.run(debug=True, host='0.0.0.0', port=5000)
