import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:5000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true
});

// 登录并获取项目列表的完整测试流程
async function verifyProjectsFix() {
  try {
    console.log('=== 开始验证项目列表功能修复 ===');
    
    // 1. 登录获取token
    console.log('\n1. 登录系统...');
    const loginResponse = await api.post('/auth/login', {
      username: 'admin',
      password: 'admin123'
    });
    
    const token = loginResponse.data.access_token;
    console.log('✓ 登录成功，获取到token');
    
    // 设置认证token
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    
    // 2. 获取项目列表
    console.log('\n2. 获取项目列表...');
    const projectsResponse = await api.get('/projects');
    console.log('✓ 项目列表获取成功');
    console.log('响应数据结构:', Object.keys(projectsResponse.data));
    
    // 检查是否包含项目数组
    const projects = projectsResponse.data.projects || projectsResponse.data;
    if (Array.isArray(projects)) {
      console.log(`✓ 获取到 ${projects.length} 个项目`);
      if (projects.length > 0) {
        console.log('项目示例:', projects[0].name);
      }
    } else {
      console.log('项目数据:', projects);
    }
    
    console.log('\n=== 项目列表功能修复验证完成 ===');
    console.log('✓ 验证结果: 成功');
    
  } catch (error) {
    console.error('\n=== 验证失败 ===');
    console.error('错误状态码:', error.response?.status);
    console.error('错误数据:', error.response?.data);
    console.error('错误信息:', error.message);
  }
}

// 运行验证
verifyProjectsFix();