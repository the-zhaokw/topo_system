const axios = require('axios');

async function testDetailedAPI() {
  try {
    console.log('开始测试API...');
    
    // 测试登录获取token
    console.log('尝试登录...');
    const loginResponse = await axios.post('http://localhost:5000/api/v1/auth/login', {
      username: 'admin',
      password: 'admin123'
    }, {
      timeout: 5000
    });
    
    console.log('登录响应状态:', loginResponse.status);
    console.log('登录响应数据:', JSON.stringify(loginResponse.data, null, 2));
    
    const token = loginResponse.data.access_token;
    console.log('获取到token:', token ? '成功' : '失败');
    
    if (!token) {
      console.log('未获取到token，无法继续测试');
      return;
    }
    
    // 使用token测试项目API
    console.log('使用token测试项目API...');
    const projectsResponse = await axios.get('http://localhost:5000/api/v1/projects', {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      timeout: 5000
    });
    
    console.log('项目API响应状态:', projectsResponse.status);
    console.log('项目API响应数据:', JSON.stringify(projectsResponse.data, null, 2));
    
  } catch (error) {
    console.error('API测试失败:');
    if (error.response) {
      console.error('响应状态:', error.response.status);
      console.error('响应头:', JSON.stringify(error.response.headers, null, 2));
      console.error('响应数据:', JSON.stringify(error.response.data, null, 2));
    } else if (error.request) {
      console.error('请求信息:', error.request);
    } else {
      console.error('错误信息:', error.message);
    }
  }
}

testDetailedAPI();