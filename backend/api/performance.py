"""
性能优化模块
- 数据库查询优化
- 简单缓存机制
- 查询性能监控
"""
from flask import Blueprint, request, jsonify, current_app
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from datetime import datetime, timedelta
import time
import json
import hashlib

perf_bp = Blueprint('performance', __name__, url_prefix='/perf')
perf_api = Api(perf_bp)

# 简单内存缓存（生产环境应使用 Redis）
_cache = {}
_cache_stats = {'hits': 0, 'misses': 0}

def cache_key(prefix, *args, **kwargs):
    """生成缓存键"""
    key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True, default=str)
    return f"{prefix}:{hashlib.md5(key_data.encode()).hexdigest()}"

def cache_get(key):
    """获取缓存"""
    if key in _cache:
        entry = _cache[key]
        if entry['expires'] > datetime.now():
            _cache_stats['hits'] += 1
            return entry['value']
        else:
            del _cache[key]
    _cache_stats['misses'] += 1
    return None

def cache_set(key, value, ttl=300):
    """设置缓存，默认5分钟"""
    _cache[key] = {
        'value': value,
        'expires': datetime.now() + timedelta(seconds=ttl)
    }

def cache_clear(prefix=None):
    """清除缓存"""
    global _cache
    if prefix:
        _cache = {k: v for k, v in _cache.items() if not k.startswith(prefix)}
    else:
        _cache = {}

def cached(ttl=300, prefix='api'):
    """缓存装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # 生成缓存键
            key = cache_key(prefix, f.__name__, *args, **kwargs)
            
            # 尝试获取缓存
            cached_value = cache_get(key)
            if cached_value is not None:
                return cached_value
            
            # 执行原函数
            result = f(*args, **kwargs)
            
            # 缓存结果
            cache_set(key, result, ttl)
            
            return result
        return decorated
    return decorator

def invalidate_cache(prefix):
    """清除指定前缀的缓存"""
    cache_clear(prefix)

# ========== 性能监控装饰器 ==========

def monitor_performance(f):
    """监控 API 性能"""
    @wraps(f)
    def decorated(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            
            # 记录性能数据
            duration = time.time() - start_time
            
            # 存储性能日志（实际项目中应存入数据库或发送到监控系统）
            if duration > 1.0:  # 记录慢查询（超过1秒）
                print(f"[SLOW QUERY] {f.__name__}: {duration:.3f}s")
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            print(f"[ERROR] {f.__name__}: {duration:.3f}s - {e}")
            raise
    
    return decorated

# ========== 数据库查询优化 ==========

def optimize_query(query, model, eager_load=None):
    """
    优化数据库查询
    - 添加选择性加载
    - 限制返回字段
    """
    if eager_load:
        from sqlalchemy.orm import joinedload
        for relation in eager_load:
            query = query.options(joinedload(getattr(model, relation)))
    
    return query

def paginate_optimized(query, page=1, per_page=20, max_per_page=100):
    """优化的分页查询"""
    per_page = min(per_page, max_per_page)
    
    # 先获取总数（使用 count 子查询优化）
    from sqlalchemy import func
    total = query.with_entities(func.count()).scalar()
    
    # 分页查询
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }

# ========== API 路由 ==========

class CacheStatsResource(Resource):
    """缓存统计 API"""
    
    method_decorators = {'get': [jwt_required()]}
    
    def get(self):
        """获取缓存统计信息"""
        # 权限检查
        from enhanced_app import User, db
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user or user.role != 'admin':
            return {'error': '权限不足'}, 403
        
        total_keys = len(_cache)
        hit_rate = 0
        total_requests = _cache_stats['hits'] + _cache_stats['misses']
        if total_requests > 0:
            hit_rate = (_cache_stats['hits'] / total_requests) * 100
        
        # 计算内存占用（估算）
        memory_usage = sum(len(str(v['value'])) for v in _cache.values())
        
        return {
            'total_keys': total_keys,
            'hits': _cache_stats['hits'],
            'misses': _cache_stats['misses'],
            'hit_rate': round(hit_rate, 2),
            'memory_usage_bytes': memory_usage,
            'memory_usage_mb': round(memory_usage / 1024 / 1024, 2)
        }

class CacheClearResource(Resource):
    """清除缓存 API"""
    
    method_decorators = {'post': [jwt_required()]}
    
    def post(self):
        """清除缓存"""
        # 权限检查
        from enhanced_app import User, db
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user or user.role != 'admin':
            return {'error': '权限不足'}, 403
        
        data = request.get_json() or {}
        prefix = data.get('prefix')
        
        cleared_count = len(_cache)
        cache_clear(prefix)
        
        if prefix:
            cleared_count = cleared_count - len(_cache)
        
        return {
            'message': '缓存已清除',
            'cleared_keys': cleared_count,
            'prefix': prefix
        }

class PerformanceMetricsResource(Resource):
    """性能指标 API"""
    
    method_decorators = {'get': [jwt_required()]}
    
    def get(self):
        """获取系统性能指标"""
        from enhanced_app import User, db
        from sqlalchemy import func
        
        # 权限检查
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user or user.role != 'admin':
            return {'error': '权限不足'}, 403
        
        # 数据库统计
        metrics = {}
        
        try:
            # 各表记录数
            metrics['database'] = {
                'bugs': db.session.query(func.count(Bug.id)).scalar(),
                'projects': db.session.query(func.count(Project.id)).scalar(),
                'users': db.session.query(func.count(UserModel.id)).scalar(),
                'tasks': 0
            }
        except Exception as e:
            metrics['database_error'] = str(e)
        
        # 系统信息
        import psutil
        metrics['system'] = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_available_mb': psutil.virtual_memory().available // 1024 // 1024,
            'disk_usage_percent': psutil.disk_usage('/').percent
        }
        
        return metrics

class DatabaseOptimizationResource(Resource):
    """数据库优化 API"""
    
    method_decorators = {'post': [jwt_required()]}
    
    def post(self):
        """执行数据库优化"""
        from enhanced_app import db, User
        
        # 权限检查
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        
        if not user or user.role != 'admin':
            return {'error': '权限不足'}, 403
        
        data = request.get_json() or {}
        operation = data.get('operation', 'analyze')
        
        results = []
        
        if operation == 'analyze':
            # SQLite ANALYZE
            try:
                db.session.execute(text('ANALYZE'))
                results.append('数据库分析完成')
            except Exception as e:
                results.append(f'分析失败: {e}')
        
        elif operation == 'vacuum':
            # SQLite VACUUM（需要单独连接）
            try:
                import sqlite3
                db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
                conn = sqlite3.connect(db_path)
                conn.execute('VACUUM')
                conn.close()
                results.append('数据库压缩完成')
            except Exception as e:
                results.append(f'压缩失败: {e}')
        
        elif operation == 'index':
            # 检查索引
            try:
                result = db.session.execute(text('SELECT name FROM sqlite_master WHERE type="index"'))
                indexes = [row[0] for row in result]
                results.append(f'现有索引: {len(indexes)} 个')
                results.extend(indexes[:10])  # 显示前10个
            except Exception as e:
                results.append(f'索引检查失败: {e}')
        
        return {
            'operation': operation,
            'results': results
        }

# 注册路由
perf_api.add_resource(CacheStatsResource, '/cache/stats')
perf_api.add_resource(CacheClearResource, '/cache/clear')
perf_api.add_resource(PerformanceMetricsResource, '/metrics')
perf_api.add_resource(DatabaseOptimizationResource, '/database/optimize')

from sqlalchemy import text
