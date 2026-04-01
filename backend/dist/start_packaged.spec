# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

spec_dir = os.path.dirname(os.path.abspath(SPEC))
project_root = os.path.dirname(os.path.dirname(spec_dir))
backend_dir = os.path.join(project_root, 'backend')
api_dir = os.path.join(backend_dir, 'api')
models_dir = os.path.join(backend_dir, 'models')
services_dir = os.path.join(backend_dir, 'services')

a = Analysis(
    ['start_packaged.py'],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join(backend_dir, 'instance'), 'instance'),
        (os.path.join(backend_dir, 'uploads'), 'uploads'),
        (api_dir, 'api'),
        (models_dir, 'models'),
        (services_dir, 'services'),
        (os.path.join(backend_dir, 'enhanced_app.py'), '.'),
        (os.path.join(backend_dir, 'run_app.py'), '.'),
        (os.path.join(backend_dir, 'restful_api.py'), '.'),
        (os.path.join(backend_dir, 'websocket_notifications.py'), '.'),
        (os.path.join(backend_dir, 'logging_config.py'), '.'),
        (os.path.join(backend_dir, 'logging_decorators.py'), '.'),
        (os.path.join(backend_dir, 'state_machine.py'), '.'),
        ('init_on_install.py', '.'),
    ],
    hiddenimports=[
        'flask',
        'flask_sqlalchemy',
        'flask_jwt_extended',
        'flask_cors',
        'flask_mail',
        'werkzeug',
        'sqlalchemy',
        'pyjwt',
        'dotenv',
        'email_validator',
        'openpyxl',
        'PIL',
        'psutil',
        'markupsafe',
        'jinja2',
        'itsdangerous',
        'click',
        'colorama',
        'bcrypt',
        'cryptography',
        'python_dotenv',
        'gevent',
        'geventwebsocket',
        'flask_socketio',
        'socketio',
        'eventlet',
        'flask_socketio',
        'pymysql',
        'mysql.connector',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'test',
        'unittest',
        'numpy',
        'scipy',
        'matplotlib',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TOPOSystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='TOPOSystem_Final',
)
