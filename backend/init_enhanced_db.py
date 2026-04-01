#!/usr/bin/env python3
"""
Enhanced Bug Management System - Database Initialization
This script initializes the enhanced database with sample data
"""

import os
import sys
import json
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash

# Add the parent directory to the path to import from enhanced_app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_app import app, db, User, Project, Bug, Comment, Activity, Notification, MaterialCategory, Material, Warehouse, Location, Inventory, SerialNumber, InventoryTransaction, MaterialRelationship
from state_machine import BugStatus, BugPriority, BugSeverity

def init_enhanced_database():
    """Initialize the enhanced database with sample data"""
    
    with app.app_context():
        # Drop all tables and recreate
        print("Dropping existing tables...")
        db.drop_all()
        
        print("Creating enhanced tables...")
        db.create_all()
        
        # Create sample users with different roles
        print("Creating sample users...")
        users = [
            User(
                username='admin',
                email='admin@bugtracker.com',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                created_at=datetime.now(timezone.utc)
            ),
            User(
                username='project_manager',
                email='pm@bugtracker.com',
                password_hash=generate_password_hash('pm123'),
                role='project_manager',
                created_at=datetime.now(timezone.utc)
            ),
            User(
                username='developer1',
                email='dev1@bugtracker.com',
                password_hash=generate_password_hash('dev123'),
                role='developer',
                created_at=datetime.now(timezone.utc)
            ),
            User(
                username='developer2',
                email='dev2@bugtracker.com',
                password_hash=generate_password_hash('dev123'),
                role='developer',
                created_at=datetime.now(timezone.utc)
            ),
            User(
                username='tester1',
                email='tester1@bugtracker.com',
                password_hash=generate_password_hash('test123'),
                role='tester',
                created_at=datetime.now(timezone.utc)
            ),
            User(
                username='guest',
                email='guest@bugtracker.com',
                password_hash=generate_password_hash('guest123'),
                role='guest',
                created_at=datetime.now(timezone.utc)
            )
        ]
        
        for user in users:
            db.session.add(user)
        db.session.commit()
        
        # Create sample projects
        print("Creating sample projects...")
        projects = [
            Project(
                name='Bug管理系统',
                description='Bug跟踪和管理系统开发项目',
                owner_id=users[0].id,  # admin
                status='active',
                code='BUG-MGMT',
                created_at=datetime.now(timezone.utc) - timedelta(days=30)
            ),
            Project(
                name='物料管理系统',
                description='企业物料库存管理系统',
                owner_id=users[1].id,  # project_manager
                status='active',
                code='MATERIAL-MGMT',
                created_at=datetime.now(timezone.utc) - timedelta(days=7)
            ),
            Project(
                name='客户关系管理系统',
                description='客户关系管理和销售跟踪系统',
                owner_id=users[0].id,  # admin
                status='active',
                code='CRM-SYSTEM',
                created_at=datetime.now(timezone.utc) - timedelta(days=120)
            )
        ]
        
        for project in projects:
            db.session.add(project)
        db.session.commit()
        
        # Create sample bugs
        print("Creating sample bugs...")
        bugs = [
            Bug(
                title='登录页面无法正常显示',
                description='用户登录页面在Chrome浏览器中无法正常显示，页面布局错乱',
                status='new',
                priority='high',
                severity='medium',
                category='UI',
                reporter_id=users[4].id,  # tester1
                assignee_id=users[2].id,  # developer1
                project_id=1,
                version='v1.0.0',
                tags=json.dumps(['UI', '登录']),
                issue_type='缺陷',
                reproduce_frequency='总是',
                found_build='v1.0.0',
                test_version='v1.0.0',
                module='前端',
                created_at=datetime.now(timezone.utc) - timedelta(days=3)
            ),
            Bug(
                title='数据保存失败',
                description='在项目详情页面修改数据后点击保存，提示保存成功但数据未实际更新',
                status='assigned',
                priority='medium',
                severity='high',
                category='功能',
                reporter_id=users[4].id,  # tester1
                assignee_id=users[3].id,  # developer2
                project_id=1,
                version='v1.0.0',
                tags=json.dumps(['后端', '数据']),
                issue_type='缺陷',
                reproduce_frequency='总是',
                found_build='v1.0.0',
                test_version='v1.0.0',
                module='后端',
                created_at=datetime.now(timezone.utc) - timedelta(days=2)
            ),
            Bug(
                title='性能优化建议',
                description='项目列表页面加载速度较慢，建议优化数据库查询',
                status='new',
                priority='low',
                severity='low',
                category='性能',
                reporter_id=users[1].id,  # project_manager
                project_id=1,
                version='v1.0.0',
                tags=json.dumps(['性能', '优化']),
                issue_type='改进',
                reproduce_frequency='总是',
                found_build='v1.0.0',
                test_version='v1.0.0',
                module='后端',
                created_at=datetime.now(timezone.utc) - timedelta(days=1)
            ),
            Bug(
                title='权限验证问题',
                description='普通用户能够访问管理员功能页面',
                status='fixed',
                priority='high',
                severity='critical',
                category='安全',
                reporter_id=users[4].id,  # tester1
                assignee_id=users[2].id,  # developer1
                resolver_id=users[2].id,  # developer1
                project_id=1,
                version='v1.0.0',
                tags=json.dumps(['安全', '权限']),
                issue_type='缺陷',
                reproduce_frequency='总是',
                found_build='v1.0.0',
                test_version='v1.0.0',
                module='后端',
                resolved_at=datetime.now(timezone.utc) - timedelta(days=1),
                created_at=datetime.now(timezone.utc) - timedelta(days=2)
            ),
            Bug(
                title='导出功能异常',
                description='项目数据导出功能在数据量较大时会出现内存溢出',
                status='verified',
                priority='medium',
                severity='medium',
                category='功能',
                reporter_id=users[1].id,  # project_manager
                assignee_id=users[3].id,  # developer2
                resolver_id=users[3].id,  # developer2
                verifier_id=users[4].id,  # tester1
                project_id=1,
                version='v1.0.0',
                tags=json.dumps(['导出', '内存']),
                issue_type='缺陷',
                reproduce_frequency='有时',
                found_build='v1.0.0',
                test_version='v1.0.0',
                module='后端',
                resolved_at=datetime.now(timezone.utc) - timedelta(days=1),
                created_at=datetime.now(timezone.utc) - timedelta(days=3)
            )
        ]
        
        for bug in bugs:
            db.session.add(bug)
        db.session.commit()
        
        # Create sample comments (removed all comments related to the three specific projects)
        comments = []
        
        for comment in comments:
            db.session.add(comment)
        db.session.commit()
        
        # Create sample activities
        print("Creating sample activities...")
        activities = [
            Activity(
                bug_id=bugs[0].id,
                user_id=users[4].id,  # tester1
                action='created',
                old_value='',
                new_value='创建了Bug',
                created_at=bugs[0].created_at
            ),
            Activity(
                bug_id=bugs[0].id,
                user_id=users[2].id,  # developer1
                action='assigned',
                old_value='',
                new_value=f'分配给 {users[2].username}',
                created_at=datetime.now(timezone.utc) - timedelta(days=2)
            ),
            Activity(
                bug_id=bugs[1].id,
                user_id=users[4].id,  # tester1
                action='created',
                old_value='',
                new_value='创建了Bug',
                created_at=bugs[1].created_at
            ),
            Activity(
                bug_id=bugs[1].id,
                user_id=users[3].id,  # developer2
                action='status_changed',
                old_value='new',
                new_value='assigned',
                created_at=datetime.now(timezone.utc) - timedelta(days=1)
            ),
            Activity(
                bug_id=bugs[3].id,
                user_id=users[3].id,  # developer2
                action='status_changed',
                old_value='in_progress',
                new_value='fixed',
                created_at=datetime.now(timezone.utc) - timedelta(days=1)
            ),
            Activity(
                bug_id=bugs[3].id,
                user_id=users[4].id,  # tester1
                action='status_changed',
                old_value='fixed',
                new_value='verified',
                created_at=datetime.now(timezone.utc) - timedelta(hours=12)
            ),
            Activity(
                bug_id=bugs[3].id,
                user_id=users[4].id,  # tester1
                action='status_changed',
                old_value='verified',
                new_value='closed',
                created_at=datetime.now(timezone.utc) - timedelta(hours=6)
            )
        ]
        
        for activity in activities:
            db.session.add(activity)
        db.session.commit()
        
        # Create sample notifications
        print("Creating sample notifications...")
        notifications = [
            Notification(
                user_id=users[2].id,  # developer1
                type='bug_assigned',
                title='Bug分配通知',
                content=f'您被分配了一个新的Bug: {bugs[0].title}',
                is_read=False,
                created_at=datetime.now(timezone.utc) - timedelta(days=2)
            ),
            Notification(
                user_id=users[3].id,  # developer2
                type='bug_assigned',
                title='Bug分配通知',
                content=f'您被分配了一个新的Bug: {bugs[1].title}',
                is_read=True,
                created_at=datetime.now(timezone.utc) - timedelta(days=2)
            ),
            Notification(
                user_id=users[4].id,  # tester1
                type='bug_status_changed',
                title='Bug状态更新',
                content=f'Bug "{bugs[3].title}" 已修复并验证通过',
                is_read=False,
                created_at=datetime.now(timezone.utc) - timedelta(hours=6)
            ),
            Notification(
                user_id=users[2].id,  # developer1
                type='bug_status_changed',
                title='Bug状态更新',
                content=f'Bug "{bugs[4].title}" 已验证通过',
                is_read=False,
                created_at=datetime.now(timezone.utc) - timedelta(days=2)
            )
        ]
        
        for notification in notifications:
            db.session.add(notification)
        db.session.commit()
        
        # Create material management system sample data
        print("Creating material management system data...")
        
        # Create material categories
        categories = [
            MaterialCategory(name='通信设备', code='COMM', description='通信网络设备', level=1),
            MaterialCategory(name='板卡', code='CARD', parent_id=1, description='设备板卡', level=2),
            MaterialCategory(name='业务板卡', code='BUSINESS_CARD', parent_id=2, description='业务处理板卡', level=3),
            MaterialCategory(name='光通信', code='OPTICAL', description='光通信设备', level=1),
            MaterialCategory(name='光模块', code='OPTICAL_MODULE', parent_id=4, description='光模块', level=2),
            MaterialCategory(name='SFP28', code='SFP28', parent_id=5, description='25G光模块', level=3),
            MaterialCategory(name='光纤', code='FIBER', parent_id=4, description='光纤线缆', level=2),
        ]
        
        for category in categories:
            db.session.add(category)
        db.session.commit()
        
        # Create materials
        materials = [
            Material(
                material_code='CARD-001',
                name='10G业务板卡',
                category_id=3,  # 业务板卡
                specification='10G业务处理板卡，支持L2VPN业务',
                brand='华为',
                unit='块',
                supplier='华为技术有限公司',
                type_specific_attrs={
                    'hardware_version': 'V2.0',
                    'software_version': 'V1.5',
                    'port_count': 4,
                    'supported_protocols': ['L2VPN', 'L3VPN', 'MPLS']
                },
                is_serialized=True,
                safety_stock=5
            ),
            Material(
                material_code='OPT-001',
                name='10G SFP+光模块',
                category_id=6,  # SFP28
                specification='10G SFP+光模块，1310nm，10km',
                brand='海信',
                unit='个',
                supplier='海信宽带多媒体技术有限公司',
                type_specific_attrs={
                    'rate': '10G',
                    'wavelength': '1310nm',
                    'distance': '10km',
                    'interface': 'LC',
                    'ddm_support': True
                },
                is_serialized=True,
                safety_stock=20
            ),
            Material(
                material_code='FIBER-001',
                name='单模光纤',
                category_id=7,  # 光纤
                specification='单模光纤，12芯，室外铠装',
                brand='长飞',
                unit='米',
                supplier='长飞光纤光缆股份有限公司',
                type_specific_attrs={
                    'type': '单模',
                    'core_count': 12,
                    'length': '标准',
                    'connector_type': 'LC/SC'
                },
                is_serialized=False,
                safety_stock=100
            ),
            Material(
                material_code='CARD-002',
                name='25G业务板卡',
                category_id=3,  # 业务板卡
                specification='25G业务处理板卡，支持高速业务',
                brand='中兴',
                unit='块',
                supplier='中兴通讯股份有限公司',
                type_specific_attrs={
                    'hardware_version': 'V3.0',
                    'software_version': 'V2.1',
                    'port_count': 8,
                    'supported_protocols': ['L2VPN', 'L3VPN', 'SRv6']
                },
                is_serialized=True,
                safety_stock=3
            ),
        ]
        
        for material in materials:
            db.session.add(material)
        db.session.commit()
        
        # Create warehouses
        warehouses = [
            Warehouse(code='WH001', name='中心仓库', address='北京市海淀区', contact_person='张经理', contact_phone='13800138001'),
            Warehouse(code='WH002', name='华北区域仓库', address='天津市滨海新区', contact_person='李主管', contact_phone='13800138002'),
            Warehouse(code='WH003', name='现场备件库', address='河北省石家庄市', contact_person='王技术', contact_phone='13800138003'),
        ]
        
        for warehouse in warehouses:
            db.session.add(warehouse)
        db.session.commit()
        
        # Create locations
        locations = [
            Location(warehouse_id=1, location_code='A-01-01', name='A区01排01位', area='A区', zone='01', rack='01', level='01', capacity=100),
            Location(warehouse_id=1, location_code='A-01-02', name='A区01排02位', area='A区', zone='01', rack='02', level='01', capacity=100),
            Location(warehouse_id=1, location_code='B-02-01', name='B区02排01位', area='B区', zone='02', rack='01', level='01', capacity=50),
            Location(warehouse_id=2, location_code='C-01-01', name='C区01排01位', area='C区', zone='01', rack='01', level='01', capacity=80),
            Location(warehouse_id=3, location_code='D-01-01', name='D区01排01位', area='D区', zone='01', rack='01', level='01', capacity=30),
        ]
        
        for location in locations:
            db.session.add(location)
        db.session.commit()
        
        # Create inventory
        inventory_items = [
            Inventory(material_id=1, warehouse_id=1, location_id=1, quantity=8, locked_quantity=0),
            Inventory(material_id=2, warehouse_id=1, location_id=2, quantity=25, locked_quantity=0),
            Inventory(material_id=3, warehouse_id=1, location_id=3, quantity=150, locked_quantity=0),
            Inventory(material_id=4, warehouse_id=2, location_id=4, quantity=2, locked_quantity=0),
            Inventory(material_id=2, warehouse_id=3, location_id=5, quantity=10, locked_quantity=0),
        ]
        
        for item in inventory_items:
            db.session.add(item)
        db.session.commit()
        
        # Create serial numbers
        serial_numbers = [
            SerialNumber(serial_number='SN-CARD-001', material_id=1, current_status='in_stock', current_location_id=1, supplier_batch='BATCH-2024-001', purchase_date=datetime.now(timezone.utc) - timedelta(days=30)),
        SerialNumber(serial_number='SN-CARD-002', material_id=1, current_status='in_stock', current_location_id=1, supplier_batch='BATCH-2024-001', purchase_date=datetime.now(timezone.utc) - timedelta(days=30)),
        SerialNumber(serial_number='SN-OPT-001', material_id=2, current_status='in_stock', current_location_id=2, supplier_batch='BATCH-2024-002', purchase_date=datetime.now(timezone.utc) - timedelta(days=20)),
        SerialNumber(serial_number='SN-OPT-002', material_id=2, current_status='in_stock', current_location_id=2, supplier_batch='BATCH-2024-002', purchase_date=datetime.now(timezone.utc) - timedelta(days=20)),
        SerialNumber(serial_number='SN-CARD-003', material_id=4, current_status='in_stock', current_location_id=4, supplier_batch='BATCH-2024-003', purchase_date=datetime.now(timezone.utc) - timedelta(days=15)),
        ]
        
        for sn in serial_numbers:
            db.session.add(sn)
        db.session.commit()
        
        # Create inventory transactions
        transactions = [
            InventoryTransaction(
                transaction_type='purchase_in',
                material_id=1,
                serial_number_id=1,
                to_warehouse_id=1,
                to_location_id=1,
                quantity=1,
                reference_id='PO-2024-001',
                remarks='采购入库',
                created_by='admin',
                created_at=datetime.now(timezone.utc) - timedelta(days=30)
            ),
            InventoryTransaction(
                transaction_type='purchase_in',
                material_id=2,
                serial_number_id=3,
                to_warehouse_id=1,
                to_location_id=2,
                quantity=1,
                reference_id='PO-2024-002',
                remarks='采购入库',
                created_by='admin',
                created_at=datetime.now(timezone.utc) - timedelta(days=25)
            ),
            InventoryTransaction(
                transaction_type='transfer',
                material_id=2,
                from_warehouse_id=1,
                from_location_id=2,
                to_warehouse_id=3,
                to_location_id=5,
                quantity=5,
                reference_id='TR-2024-001',
                remarks='调拨到现场备件库',
                created_by='project_manager',
                created_at=datetime.now(timezone.utc) - timedelta(days=15)
            ),
        ]
        
        for transaction in transactions:
            db.session.add(transaction)
        db.session.commit()
        
        print("✅ Enhanced database initialized successfully!")
        print(f"Created {len(users)} users")
        print(f"Created {len(projects)} projects")
        print(f"Created {len(bugs)} bugs")
        print(f"Created {len(comments)} comments")
        print(f"Created {len(activities)} activities")
        print(f"Created {len(notifications)} notifications")
        print(f"Created {len(categories)} material categories")
        print(f"Created {len(materials)} materials")
        print(f"Created {len(warehouses)} warehouses")
        print(f"Created {len(locations)} locations")
        print(f"Created {len(inventory_items)} inventory items")
        print(f"Created {len(serial_numbers)} serial numbers")
        print(f"Created {len(transactions)} inventory transactions")
        print("\n📋 Sample login credentials:")
        print("- Admin: admin / admin123")
        print("- Project Manager: project_manager / pm123")
        print("- Developer: developer1 / dev123")
        print("- Tester: tester1 / test123")
        print("- Guest: guest / guest123")
        print("\n📦 Material Management System:")
        print("- Material Categories: 通信设备 -> 板卡 -> 业务板卡, 光通信 -> 光模块 -> SFP28, 光纤")
        print("- Materials: 10G业务板卡, 25G业务板卡, 10G SFP+光模块, 单模光纤")
        print("- Warehouses: 中心仓库, 华北区域仓库, 现场备件库")

if __name__ == '__main__':
    init_enhanced_database()