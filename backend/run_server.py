"""启动后端服务"""
import os
os.chdir(r'd:\topo_system\backend')
from enhanced_app import app, register_api_blueprints, init_db, init_extensions

if __name__ == '__main__':
    init_extensions(app)
    init_db()
    register_api_blueprints()
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
