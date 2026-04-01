#!/usr/bin/env python3
"""
TOPO系统 - 自动化演示脚本
用于系统演示和培训的自动化脚本
"""

import requests
import json
import time
import sys
from datetime import datetime

class BugSystemDemo:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        
        # 演示数据
        self.demo_users = {
            "admin": {"username": "admin", "password": "admin123", "role": "admin"},
            "project_manager": {"username": "project_manager", "password": "project123", "role": "project_manager"},
            "developer": {"username": "developer1", "password": "dev123", "role": "developer"},
            "tester": {"username": "tester1", "password": "test123", "role": "tester"}
        }
        
        self.demo_project = {
            "name": "演示项目",
            "description": "系统演示和培训用项目",
            "status": "active"
        }
        
        self.demo_bugs = [
            {
                "title": "购物车页面加载缓慢",
                "description": "用户添加商品到购物车后，页面响应时间超过5秒",
                "severity": "high",
                "priority": "high",
                "status": "open"
            },
            {
                "title": "支付页面SSL证书错误",
                "description": "部分用户反映支付页面显示SSL证书不安全警告",
                "severity": "critical",
                "priority": "high",
                "status": "in_progress"
            },
            {
                "title": "商品搜索功能不准确",
                "description": "搜索结果与搜索关键词匹配度不高",
                "severity": "medium",
                "priority": "medium",
                "status": "resolved"
            }
        ]
    
    def print_step(self, step_number, description):
        """打印演示步骤"""
        print(f"\n{'='*60}")
        print(f"步骤 {step_number}: {description}")
        print(f"{'='*60}")
    
    def login(self, username, password):
        """用户登录"""
        url = f"{self.base_url}/api/auth/login"
        data = {
            "username": username,
            "password": password
        }
        
        try:
            response = self.session.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                self.token = result.get("token")
                print(f"✓ {username} 登录成功")
                return True
            else:
                print(f"✗ {username} 登录失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ 登录请求失败: {e}")
            return False
    
    def create_project(self):
        """创建演示项目"""
        url = f"{self.base_url}/api/projects"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = self.session.post(url, json=self.demo_project, headers=headers)
            if response.status_code == 201:
                project_data = response.json()
                print(f"✓ 项目创建成功: {project_data['name']} (ID: {project_data['id']})")
                return project_data['id']
            else:
                print(f"✗ 项目创建失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"✗ 项目创建请求失败: {e}")
            return None
    
    def create_bug(self, project_id, bug_data, assigned_to=None):
        """创建Bug报告"""
        url = f"{self.base_url}/api/bugs"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        bug_data = bug_data.copy()
        bug_data["project_id"] = project_id
        if assigned_to:
            bug_data["assigned_to"] = assigned_to
        
        try:
            response = self.session.post(url, json=bug_data, headers=headers)
            if response.status_code == 201:
                bug_data = response.json()
                print(f"✓ Bug创建成功: {bug_data['title']} (ID: {bug_data['id']})")
                return bug_data['id']
            else:
                print(f"✗ Bug创建失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"✗ Bug创建请求失败: {e}")
            return None
    
    def update_bug_status(self, bug_id, new_status):
        """更新Bug状态"""
        url = f"{self.base_url}/api/bugs/{bug_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        update_data = {"status": new_status}
        
        try:
            response = self.session.put(url, json=update_data, headers=headers)
            if response.status_code == 200:
                print(f"✓ Bug状态更新成功: {bug_id} -> {new_status}")
                return True
            else:
                print(f"✗ Bug状态更新失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Bug状态更新请求失败: {e}")
            return False
    
    def export_data(self, data_type, format_type):
        """导出数据"""
        url = f"{self.base_url}/api/{data_type}/export?format={format_type}"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = self.session.get(url, headers=headers)
            if response.status_code == 200:
                file_size = len(response.content)
                content_type = response.headers.get("Content-Type", "未知")
                print(f"✓ {data_type} {format_type}导出成功: {file_size}字节, 类型: {content_type}")
                return True
            else:
                print(f"✗ {data_type} {format_type}导出失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ 导出请求失败: {e}")
            return False
    
    def get_statistics(self):
        """获取统计信息"""
        url = f"{self.base_url}/api/stats"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = self.session.get(url, headers=headers)
            if response.status_code == 200:
                stats = response.json()
                print(f"✓ 统计信息获取成功:")
                print(f"   - 项目总数: {stats.get('total_projects', 0)}")
                print(f"   - Bug总数: {stats.get('total_bugs', 0)}")
                print(f"   - 用户总数: {stats.get('total_users', 0)}")
                return True
            else:
                print(f"✗ 统计信息获取失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ 统计信息请求失败: {e}")
            return False
    
    def run_full_demo(self):
        """运行完整演示"""
        print("🚀 TOPO系统 - 自动化演示开始")
        print(f"📅 演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 步骤1: 管理员登录和系统概览
        self.print_step(1, "管理员登录和系统概览")
        if not self.login("admin", "admin123"):
            print("❌ 演示终止: 管理员登录失败")
            return False
        
        time.sleep(1)
        
        # 步骤2: 创建演示项目
        self.print_step(2, "创建演示项目")
        project_id = self.create_project()
        if not project_id:
            print("❌ 演示终止: 项目创建失败")
            return False
        
        time.sleep(1)
        
        # 步骤3: 测试人员创建Bug报告
        self.print_step(3, "测试人员创建Bug报告")
        if not self.login("tester1", "test123"):
            print("❌ 演示终止: 测试人员登录失败")
            return False
        
        bug_ids = []
        for i, bug_data in enumerate(self.demo_bugs):
            bug_id = self.create_bug(project_id, bug_data, "developer1")
            if bug_id:
                bug_ids.append(bug_id)
            time.sleep(0.5)
        
        if not bug_ids:
            print("❌ 演示终止: 没有Bug创建成功")
            return False
        
        time.sleep(1)
        
        # 步骤4: 开发人员处理Bug
        self.print_step(4, "开发人员处理Bug")
        if not self.login("developer1", "dev123"):
            print("❌ 演示终止: 开发人员登录失败")
            return False
        
        # 更新第一个Bug状态为进行中
        if bug_ids:
            self.update_bug_status(bug_ids[0], "in_progress")
            time.sleep(0.5)
            self.update_bug_status(bug_ids[0], "resolved")
        
        time.sleep(1)
        
        # 步骤5: 测试人员验证Bug
        self.print_step(5, "测试人员验证Bug")
        if not self.login("tester1", "test123"):
            print("❌ 演示终止: 测试人员登录失败")
            return False
        
        # 验证并关闭已解决的Bug
        if len(bug_ids) > 2:
            self.update_bug_status(bug_ids[2], "closed")
        
        time.sleep(1)
        
        # 步骤6: 项目经理查看项目状态
        self.print_step(6, "项目经理查看项目状态")
        if not self.login("project_manager", "project123"):
            print("❌ 演示终止: 项目经理登录失败")
            return False
        
        self.get_statistics()
        
        time.sleep(1)
        
        # 步骤7: 数据导出功能演示
        self.print_step(7, "数据导出功能演示")
        
        # 使用管理员权限进行导出
        if not self.login("admin", "admin123"):
            print("❌ 演示终止: 管理员登录失败")
            return False
        
        # 导出各种数据格式
        export_types = [
            ("bugs", "csv"),
            ("bugs", "excel"),
            ("projects", "csv"),
            ("projects", "excel"),
            ("users", "csv"),
            ("users", "excel")
        ]
        
        for data_type, format_type in export_types:
            self.export_data(data_type, format_type)
            time.sleep(0.3)
        
        time.sleep(1)
        
        # 步骤8: 演示总结
        self.print_step(8, "演示总结")
        print("✅ 演示完成!")
        print("📊 演示内容总结:")
        print("   - 多角色用户登录和权限控制")
        print("   - 完整的项目创建和管理流程")
        print("   - Bug生命周期管理（创建→分配→处理→验证→关闭）")
        print("   - 数据统计和分析功能")
        print("   - 多种格式的数据导出功能")
        print("\n🎯 系统亮点展示:")
        print("   - 灵活的权限管理系统")
        print("   - 完整的Bug跟踪工作流")
        print("   - 强大的数据导出和分析能力")
        print("   - 用户友好的界面设计")
        
        return True

def main():
    """主函数"""
    demo = BugSystemDemo()
    
    try:
        success = demo.run_full_demo()
        if success:
            print("\n🎉 演示成功完成!")
            sys.exit(0)
        else:
            print("\n❌ 演示过程中出现错误")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ 演示被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 演示出现异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()