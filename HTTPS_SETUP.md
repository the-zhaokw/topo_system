# TOPO System Development HTTPS Setup Guide
# ==========================================

## Option 1: Using mkcert for Local Development (Recommended for Dev)

### Step 1: Install mkcert
```bash
# On Windows (using Chocolatey)
choco install mkcert

# On macOS
brew install mkcert

# On Linux
sudo apt install libnss3-tools
brew install mkcert
```

### Step 2: Generate certificates
```bash
# In the project root
cd d:\topo_system

# Create a certificates directory
mkdir certs

# Generate certificate for localhost
mkcert -key-file certs/localhost-key.pem -cert-file certs/localhost.pem "172.18.36.249" "localhost" "127.0.0.1"
```

### Step 3: Update vite.config.js
```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    strictPort: true,
    https: {
      key: './certs/localhost-key.pem',
      cert: './certs/localhost.pem'
    },
    proxy: {
      '/api': {
        target: 'https://localhost:5000',
        changeOrigin: true,
        secure: false
      },
      '/auth': {
        target: 'https://localhost:5000',
        changeOrigin: true,
        secure: false
      },
      '/uploads': {
        target: 'https://localhost:5000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  // ... rest of config
})
```

### Step 4: Update Flask to support HTTPS
In run_app.py, modify the app.run() to use SSL:
```python
import ssl

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('./certs/localhost.pem', './certs/localhost-key.pem')

# Then in socketio.run or app.run:
socketio.run(app, debug=False, host='0.0.0.0', port=5000, use_reloader=False, ssl_context=context)
```

---

## Option 2: Production Deployment with Nginx

### Prerequisites
1. SSL Certificate (Let's Encrypt recommended)
2. Nginx installed

### Steps
1. Copy nginx.https.conf to /etc/nginx/sites-available/
2. Edit the certificate paths
3. Symlink to sites-enabled
4. Test and reload nginx

---

## Option 3: Using Docker for Development

Create docker-compose.yml:
```yaml
version: '3.8'
services:
  frontend:
    build: ./vue-frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_BASE_URL=/api
    volumes:
      - ./certs:/app/certs

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    volumes:
      - ./certs:/app/certs
```

---

## Important Notes

1. **Blob URLs**: The error `blob: http://172.18.36.249:3000/...` occurs because:
   - The page is served over HTTP
   - Blob URLs inherit the parent's insecure context
   - Solution: Always serve over HTTPS

2. **WebSocket**: If using Socket.IO, the ws:// connection also needs to be wss:// when on HTTPS

3. **For production**: Always use valid certificates (Let's Encrypt is free)

4. **CORS**: If you have CORS issues after enabling HTTPS, update your Flask CORS configuration to allow the https:// origin
