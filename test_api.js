const axios = require('axios');

async function testProjectsAPI() {
  try {
    // 测试登录获取token
    const loginResponse = await axios.post('http://localhost:5000/api/v1/auth/login', {
      username: 'admin',
      password: 'admin123'
    });
    
    const token = loginResponse.data.access_token;
    console.log('登录成功，token:', token);
    
    // 使用token测试项目API
    const projectsResponse = await axios.get('http://localhost:5000/api/v1/projects', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    console.log('项目API响应状态:', projectsResponse.status);
    console.log('项目API响应数据结构:', JSON.stringify(projectsResponse.data, null, 2));
    
    // 检查数据结构
    const data = projectsResponse.data;
    console.log('\n数据结构分析:');
    console.log('是否有projects属性:', 'projects' in data);
    console.log('projects属性类型:', typeof data.projects);
    if (Array.isArray(data.projects)) {
      console.log('projects数组长度:', data.projects.length);
      if (data.projects.length > 0) {
        console.log('第一个项目结构:', JSON.stringify(data.projects[0], null, 2));
      }
    }
    
  } catch (error) {
    console.error('API测试失败:', error.response?.data || error.message);
  }
}

testProjectsAPI();