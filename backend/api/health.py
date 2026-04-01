"""
Health Check and System Monitoring Module
"""
from flask import Blueprint, jsonify
from flask_restful import Api, Resource
from datetime import datetime
import os
import sys
from sqlalchemy import text

health_bp = Blueprint('health', __name__, url_prefix='/health')
health_api = Api(health_bp)

class HealthCheckResource(Resource):
    """Health Check API"""
    
    def get(self):
        """System health status check"""
        checks = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'checks': {}
        }
        
        # Database check
        try:
            from enhanced_app import db
            db.session.execute(text('SELECT 1'))
            checks['checks']['database'] = {'status': 'ok', 'message': 'Database connection OK'}
        except Exception as e:
            checks['checks']['database'] = {'status': 'error', 'message': str(e)}
            checks['status'] = 'unhealthy'
        
        # Disk space check
        try:
            import psutil
            disk = psutil.disk_usage('/')
            free_percent = (disk.free / disk.total) * 100
            if free_percent < 10:
                checks['checks']['disk'] = {'status': 'warning', 'message': f'Disk space low: {free_percent:.1f}% remaining'}
            else:
                checks['checks']['disk'] = {'status': 'ok', 'message': f'Disk space OK: {free_percent:.1f}% remaining'}
        except Exception as e:
            checks['checks']['disk'] = {'status': 'error', 'message': str(e)}
        
        # Memory check
        try:
            import psutil
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                checks['checks']['memory'] = {'status': 'warning', 'message': f'High memory usage: {memory.percent}%'}
            else:
                checks['checks']['memory'] = {'status': 'ok', 'message': f'Memory usage: {memory.percent}%'}
        except Exception as e:
            checks['checks']['memory'] = {'status': 'error', 'message': str(e)}
        
        status_code = 200 if checks['status'] == 'healthy' else 503
        return checks, status_code

class SystemInfoResource(Resource):
    """System Info API"""
    
    def get(self):
        """Get detailed system information"""
        info = {
            'python_version': sys.version,
            'platform': sys.platform,
            'timestamp': datetime.utcnow().isoformat(),
            'environment': {
                'FLASK_ENV': os.environ.get('FLASK_ENV', 'production'),
                'FLASK_DEBUG': os.environ.get('FLASK_DEBUG', 'False')
            }
        }
        
        # Dependency versions
        try:
            import flask
            import sqlalchemy
            import flask_jwt_extended
            info['dependencies'] = {
                'flask': flask.__version__,
                'sqlalchemy': sqlalchemy.__version__,
                'flask_jwt_extended': flask_jwt_extended.__version__
            }
        except Exception as e:
            info['dependencies_error'] = str(e)
        
        return info

class ReadinessCheckResource(Resource):
    """Readiness Check API (for K8s)"""
    
    def get(self):
        """Check if application is ready"""
        try:
            from enhanced_app import db
            db.session.execute(text('SELECT 1'))
            return {'status': 'ready'}, 200
        except Exception as e:
            return {'status': 'not_ready', 'error': str(e)}, 503

class LivenessCheckResource(Resource):
    """Liveness Check API (for K8s)"""
    
    def get(self):
        """Check if application is alive"""
        return {'status': 'alive'}, 200

# Register routes
health_api.add_resource(HealthCheckResource, '/')
health_api.add_resource(SystemInfoResource, '/info')
health_api.add_resource(ReadinessCheckResource, '/ready')
health_api.add_resource(LivenessCheckResource, '/live')
