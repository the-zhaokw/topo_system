#!/usr/bin/env python3
"""
TOPO系统 - 快速演示脚本
用于5-10分钟的简短演示场景
"""

import requests
import json
import time

class QuickDemo:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
    
    def login(self, username, password):
        """用户登录"""
        url = f"{self.base_url}/api/auth/login"
        data = {"username": username, "password": password}
        
        try:
            response = self.session.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                self.token = result.get('access_token')
                print(f"✓ {username} 登录成功")
                return True
            else:
                print(f"✗ {username} 登录失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ 登录失败: {e}")
            return False
    
    def show_dashboard(self):
        """显示仪表板信息"""
        url = f"{self.base_url}/api/statistics"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = self.session.get(url, headers=headers)
            if response.status_code == 200:
                result = response.json()
                print("📊 系统统计信息:")
                print(f"   项目总数: {result.get('total_projects', 0)}")
                print(f"   Bug总数: {result.get('total_bugs', 0)}")
                print(f"   活跃用户: {result.get('active_users', 0)}")
                return True
            else:
                print("✗ 无法获取统计信息")
                return False
        except Exception as e:
            print(f"✗ 获取统计信息失败: {e}")
            return False
    
    def list_projects(self):
        """显示项目列表"""
        print("3️⃣ 项目管理")
        
        # 获取项目列表
        url = f"{self.base_url}/api/projects"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = self.session.get(url, headers=headers)
            if response.status_code == 200:
                result = response.json()
                projects = result.get('projects', [])
                print(f"   ✓ 项目数量: {len(projects)}")
                for project in projects[:3]:  # 显示前3个项目
                    print(f"      - {project.get('name', '未知')} (状态: {project.get('status', '未知')})")
            else:
                print(f"   ✗ 项目列表API请求失败: {response.status_code}")
        except Exception as e:
            print(f"   ✗ 项目列表获取错误: {e}")
    
    def list_bugs(self):
        """显示Bug列表"""
        print("4️⃣ Bug跟踪")
        
        # 获取Bug列表
        url = f"{self.base_url}/api/bugs"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = self.session.get(url, headers=headers)
            if response.status_code == 200:
                result = response.json()
                bugs = result.get('bugs', [])
                print(f"   ✓ Bug数量: {len(bugs)}")
                for bug in bugs[:3]:  # 显示前3个Bug
                    print(f"      - {bug.get('title', '未知')} (状态: {bug.get('status', '未知')})")
            else:
                print(f"   ✗ Bug列表API请求失败: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Bug列表获取错误: {e}")
    
    def export_demo(self):
        """演示导出功能"""
        print("📤 数据导出演示:")
        
        # 导出Bug数据
        formats = ["csv", "excel"]
        for fmt in formats:
            url = f"{self.base_url}/api/bugs/export?format={fmt}"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            try:
                response = self.session.get(url, headers=headers)
                if response.status_code == 200:
                    size = len(response.content)
                    print(f"   ✓ Bug {fmt.upper()}导出: {size}字节")
                else:
                    print(f"   ✗ Bug {fmt.upper()}导出失败: {response.status_code}")
            except Exception as e:
                print(f"   ✗ Bug {fmt.upper()}导出错误: {e}")
    
    def run_quick_demo(self):
        """运行快速演示"""
        print("🚀 TOPO系统 - 快速演示开始\n")
        
        # 1. 管理员登录
        print("1️⃣ 管理员登录")
        if not self.login("admin", "admin123"):
            return False
        time.sleep(1)
        
        # 2. 显示仪表板
        print("\n2️⃣ 系统概览")
        self.show_dashboard()
        time.sleep(1)
        
        # 3. 项目列表
        print("\n3️⃣ 项目管理")
        self.list_projects()
        time.sleep(1)
        
        # 4. Bug列表
        print("\n4️⃣ Bug跟踪")
        self.list_bugs()
        time.sleep(1)
        
        # 5. 数据导出
        print("\n5️⃣ 数据导出")
        self.export_demo()
        time.sleep(1)
        
        # 演示总结
        print("\n🎯 演示总结")
        print("✅ 系统核心功能演示完成")
        print("📋 包含功能:")
        print("   - 用户认证和权限管理")
        print("   - 项目管理和跟踪")
        print("   - Bug生命周期管理")
        print("   - 数据导出和分析")
        print("\n💡 系统亮点:")
        print("   - 完整的项目管理解决方案")
        print("   - 灵活的权限控制系统")
        print("   - 强大的数据导出能力")
        
        return True

def main():
    """主函数"""
    demo = QuickDemo()
    
    try:
        success = demo.run_quick_demo()
        if success:
            print("\n🎉 快速演示成功完成!")
        else:
            print("\n❌ 演示过程中出现错误")
    except KeyboardInterrupt:
        print("\n⏹️ 演示被用户中断")
    except Exception as e:
        print(f"\n💥 演示出现异常: {e}")

if __name__ == "__main__":
    main()