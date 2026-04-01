// 检查前端认证状态
const axios = require('axios');

async function checkFrontendAuthStatus() {
  try {
    console.log('=== 检查前端认证状态 ===');
    
    // 1. 检查localStorage中是否有token（模拟前端状态）
    console.log('1. 检查前端localStorage中的token状态...');
    
    // 2. 测试后端认证状态
    console.log('2. 测试后端认证状态...');
    
    // 尝试使用admin用户登录
    const loginResponse = await axios.post('http://localhost:5000/api/v1/auth/login', {
      username: 'admin',
      password: 'admin123'
    });
    
    console.log('✅ 后端登录成功');
    const token = loginResponse.data.access_token;
    console.log('Token:', token.substring(0, 20) + '...');
    
    // 3. 测试前端API调用
    console.log('\n3. 测试前端API调用...');
    
    // 带认证的项目API调用
    const projectsResponse = await axios.get('http://localhost:5000/api/v1/projects', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    console.log('✅ 项目API调用成功');
    console.log('响应状态:', projectsResponse.status);
    console.log('项目数量:', projectsResponse.data.projects?.length || 0);
    
    // 4. 检查前端是否应该自动登录
    console.log('\n4. 前端登录状态分析:');
    console.log('   - 前端有路由守卫，需要认证才能访问Dashboard');
    console.log('   - 前端应用启动时没有自动登录机制');
    console.log('   - 用户需要手动访问登录页面进行登录');
    
    console.log('\n=== 建议 ===');
    console.log('1. 打开浏览器访问: http://localhost:3001/login');
    console.log('2. 使用以下账户登录:');
    console.log('   用户名: admin');
    console.log('   密码: admin123');
    console.log('3. 登录后会自动跳转到Dashboard页面');
    
  } catch (error) {
    console.error('❌ 检查失败:', error.message);
    if (error.response) {
      console.error('响应状态:', error.response.status);
      console.error('响应数据:', error.response.data);
    }
  }
}

checkFrontendAuthStatus();