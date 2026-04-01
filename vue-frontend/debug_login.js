import axios from 'axios';

// 配置axios实例，与前端项目配置一致
const api = axios.create({
  baseURL: 'http://localhost:5000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 添加请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('请求配置:', {
      url: config.url,
      method: config.method,
      headers: config.headers,
      data: config.data
    });
    return config;
  },
  (error) => {
    console.error('请求错误:', error.message);
    return Promise.reject(error);
  }
);

// 添加响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('响应数据:', {
      status: response.status,
      statusText: response.statusText,
      data: response.data
    });
    return response;
  },
  (error) => {
    console.error('响应错误详情:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message,
      config: error.config
    });
    return Promise.reject(error);
  }
);

// 测试登录函数
async function debugLogin() {
  try {
    console.log('=== 开始调试登录流程 ===');
    console.log('使用凭据: admin / admin123');
    
    // 模拟前端登录请求
    const response = await api.post('/auth/login', {
      username: 'admin',
      password: 'admin123'
    });
    
    console.log('登录成功!');
    console.log('Token:', response.data.access_token);
    console.log('用户信息:', response.data.user);
    
  } catch (error) {
    console.error('登录失败!');
    if (error.response) {
      // 服务器返回错误状态码
      console.error('服务器响应错误:', {
        status: error.response.status,
        data: error.response.data,
        headers: error.response.headers
      });
    } else if (error.request) {
      // 请求已发送但未收到响应
      console.error('网络请求错误:', error.request);
    } else {
      // 请求配置出错
      console.error('请求配置错误:', error.message);
    }
  }
}

// 执行调试
debugLogin().then(() => {
  console.log('=== 调试完成 ===');
});