import axios from 'axios';

// 配置axios实例
const api = axios.create({
  baseURL: 'http://localhost:5000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 测试登录API
async function testLoginApi() {
  try {
    console.log('开始测试登录API...');
    
    // 使用系统默认管理员凭据登录
    const response = await api.post('/auth/login', {
      username: 'admin',
      password: 'admin123'
    });
    
    console.log('登录成功!');
    console.log('响应状态码:', response.status);
    console.log('响应数据:', response.data);
    
    return { success: true, data: response.data };
    
  } catch (error) {
    console.error('登录失败!');
    
    if (error.response) {
      console.error('响应状态码:', error.response.status);
      console.error('响应数据:', error.response.data);
      console.error('错误信息:', error.response.data.error || error.response.data.message);
    } else if (error.request) {
      console.error('请求发送失败，没有收到响应');
      console.error('请求详情:', error.request);
    } else {
      console.error('请求配置错误:', error.message);
    }
    
    return { success: false, error: error };
  }
}

// 执行测试
testLoginApi().then(() => {
  console.log('\n测试完成');
});