// 测试前端认证状态
const axios = require('axios');

async function testFrontendAuth() {
  try {
    // 模拟前端登录
    console.log('=== 测试前端登录流程 ===');
    
    // 1. 尝试登录
    const loginResponse = await axios.post('http://localhost:5000/api/v1/auth/login', {
      username: 'admin',
      password: 'admin123'
    });
    
    console.log('登录成功:', loginResponse.status);
    const token = loginResponse.data.access_token;
    console.log('获取到的token:', token.substring(0, 20) + '...');
    
    // 2. 测试获取当前用户信息（模拟前端初始化）
    console.log('\n=== 测试获取当前用户信息 ===');
    const userResponse = await axios.get('http://localhost:5000/api/v1/auth/me', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    console.log('获取用户信息成功:', userResponse.status);
    console.log('当前用户:', JSON.stringify(userResponse.data, null, 2));
    
    // 3. 测试项目API（模拟Dashboard调用）
    console.log('\n=== 测试项目API（带认证） ===');
    const projectsResponse = await axios.get('http://localhost:5000/api/v1/projects', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    console.log('项目API响应状态:', projectsResponse.status);
    console.log('项目数量:', projectsResponse.data.projects?.length || 0);
    
    // 4. 测试项目API（不带认证）
    console.log('\n=== 测试项目API（不带认证） ===');
    try {
      const noAuthResponse = await axios.get('http://localhost:5000/api/v1/projects');
      console.log('无认证请求状态:', noAuthResponse.status);
    } catch (error) {
      console.log('无认证请求失败:', error.response?.status, error.response?.data?.error);
    }
    
  } catch (error) {
    console.error('测试失败:', error.response?.data || error.message);
  }
}

testFrontendAuth();