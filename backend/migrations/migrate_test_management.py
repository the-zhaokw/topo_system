"""
测试管理模块数据库迁移脚本
创建测试集、测试用例、测试执行等相关表
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_app import app, db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_test_management_tables():
    """创建测试管理模块所需的数据库表"""
    with app.app_context():
        try:
            logger.info("开始检查和创建测试管理模块数据库表...")
            
            # 导入所有需要的模型
            from enhanced_app import (
                TestSuite, TestCase, TestStep, 
                TestExecution, TestResult, TestCaseRequirementLink
            )
            
            # 检查表是否存在，如果不存在则创建
            tables_to_check = [
                TestSuite,
                TestCase, 
                TestStep,
                TestExecution,
                TestResult,
                TestCaseRequirementLink
            ]
            
            for model in tables_to_check:
                table_name = model.__tablename__
                inspector = db.inspect(db.engine)
                if table_name not in inspector.get_table_names():
                    logger.info(f"创建表: {table_name}")
                    model.__table__.create(db.engine)
                else:
                    logger.info(f"表 {table_name} 已存在，跳过创建")
            
            # 提交更改
            db.session.commit()
            
            logger.info("测试管理模块数据库表迁移完成！")
            return True
            
        except Exception as e:
            logger.error(f"数据库迁移失败: {str(e)}")
            db.session.rollback()
            return False


if __name__ == '__main__':
    success = migrate_test_management_tables()
    if success:
        print("✅ 测试管理模块数据库迁移成功！")
        sys.exit(0)
    else:
        print("❌ 测试管理模块数据库迁移失败！")
        sys.exit(1)
