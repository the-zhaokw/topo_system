import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:5000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    console.log('Request URL:', config.url);
    console.log('Request Method:', config.method);
    return config;
  },
  error => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log('Response Status:', response.status);
    console.log('Response Data:', response.data);
    return response;
  },
  error => {
    console.error('Response Error:', error.response ? error.response.status : 'No response');
    console.error('Error Data:', error.response ? error.response.data : error.message);
    return Promise.reject(error);
  }
);

// 测试获取项目列表
async function testProjectsApi() {
  try {
    console.log('Testing GET /projects endpoint...');
    const response = await api.get('/projects');
    console.log('\nProjects API Test Result: SUCCESS');
    console.log('Number of projects returned:', response.data.length);
    
    // 先登录获取token，然后再测试需要认证的接口
    console.log('\nTesting login first to get authentication token...');
    const loginResponse = await api.post('/auth/login', {
      email: 'admin@bugtracker.com',
      password: 'admin123'
    });
    
    // 设置认证token
    const token = loginResponse.data.access_token;
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    
    console.log('\nTesting GET /projects with authentication...');
    const authResponse = await api.get('/projects');
    console.log('Authenticated Projects API Test Result: SUCCESS');
    console.log('Number of projects returned with auth:', authResponse.data.length);
    
  } catch (error) {
    console.error('\nProjects API Test Result: FAILED');
    console.error('Error Details:', error.message);
  }
}

// 运行测试
testProjectsApi();