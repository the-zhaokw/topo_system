// 简单的API测试脚本
import axios from 'axios';

async function testLoginAPI() {
  try {
    console.log('开始测试登录API...');
    
    // 模拟前端登录请求
    const response = await axios.post('http://localhost:5000/api/v1/auth/login', {
      username: 'admin',
      password: 'admin123'
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    console.log('登录API测试成功!');
    console.log('响应状态码:', response.status);
    console.log('响应数据:', response.data);
    console.log('\n前端API路径已修复，现在可以正确访问后端服务。');
    
  } catch (error) {
    console.error('登录API测试失败:', error.message);
    if (error.response) {
      console.error('响应状态码:', error.response.status);
      console.error('响应数据:', error.response.data);
    }
  }
}

// 运行测试
testLoginAPI();