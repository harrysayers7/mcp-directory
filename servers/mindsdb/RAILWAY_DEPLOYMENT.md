# 🚀 Railway Deployment Guide for MindsDB MCP Server

## Quick Start

### 1. **Connect Repository to Railway**

1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select `harrysayers7/mcp-directory`
5. Choose "Deploy from a subdirectory"
6. Set subdirectory to `servers/mindsdb`

### 2. **Add Required Services**

#### **Redis Service**
1. In your Railway project, click "New Service"
2. Select "Database" → "Redis"
3. Railway will automatically set `REDIS_HOST` and `REDIS_PORT` environment variables

#### **MindsDB Service (Optional)**
If you want to run MindsDB on Railway too:
1. Click "New Service" → "Database" → "PostgreSQL" (for MindsDB data)
2. Or use external MindsDB Cloud

### 3. **Configure Environment Variables**

Set these in Railway dashboard:

```bash
# MindsDB Configuration
MINDSDB_API_KEY=your-mindsdb-api-key
MINDSDB_HOST=https://your-mindsdb-instance.com
MINDSDB_PORT=47334

# Redis Configuration (auto-set by Railway)
REDIS_HOST=redis.railway.internal
REDIS_PORT=6379

# Application Configuration
LOG_LEVEL=INFO
MCP_SERVER_NAME=mindsdb
MCP_SERVER_VERSION=0.1.0

# Railway will automatically set:
PORT=8000
RAILWAY_ENVIRONMENT=production
```

### 4. **Deploy**

Railway will automatically:
- Build the Docker image
- Deploy the service
- Set up health checks
- Provide a public URL

## 🔧 **Railway-Specific Optimizations**

### **Dockerfile Optimizations**
- Uses `python:3.11-slim` for smaller image size
- Multi-stage build for production optimization
- Non-root user for security
- Health check endpoint integration

### **Environment Variables**
Railway automatically provides:
- `PORT` - The port your app should listen on
- `RAILWAY_ENVIRONMENT` - Environment name
- `RAILWAY_PUBLIC_DOMAIN` - Your app's public URL

### **Health Checks**
Railway will automatically check `/health` endpoint every 30 seconds.

## 📊 **Monitoring & Logs**

### **View Logs**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# View logs
railway logs
```

### **Metrics**
Railway provides:
- CPU and memory usage
- Request count and response times
- Error rates
- Health check status

## 🔒 **Security Best Practices**

### **Environment Variables**
- Never commit API keys to git
- Use Railway's environment variable system
- Rotate keys regularly

### **Network Security**
- Railway provides HTTPS by default
- Internal services communicate securely
- No need to expose internal ports

## 🚀 **Scaling**

### **Horizontal Scaling**
Railway supports:
- Multiple replicas
- Load balancing
- Auto-scaling based on traffic

### **Vertical Scaling**
- Adjust CPU and memory limits
- Upgrade/downgrade as needed

## 💰 **Cost Optimization**

### **Resource Limits**
Set appropriate limits:
- CPU: 0.5-2 vCPU
- Memory: 512MB-2GB
- Storage: 1-10GB

### **Sleep Mode**
- Railway can sleep inactive services
- Wakes up automatically on requests
- Perfect for MCP servers

## 🔄 **CI/CD Integration**

### **Automatic Deployments**
Railway automatically deploys when you push to:
- `main` branch → Production
- `develop` branch → Staging
- Any branch → Preview deployment

### **GitHub Actions Integration**
```yaml
# .github/workflows/railway-deploy.yml
name: Deploy to Railway
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: railway-app/railway-deploy@v1
        with:
          railway-token: ${{ secrets.RAILWAY_TOKEN }}
```

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Build Failures**
   - Check Dockerfile syntax
   - Verify Python dependencies
   - Check build logs in Railway dashboard

2. **Runtime Errors**
   - Check environment variables
   - Verify Redis connection
   - Check application logs

3. **Health Check Failures**
   - Ensure `/health` endpoint is working
   - Check port configuration
   - Verify startup time

### **Debug Commands**
```bash
# Connect to Railway service
railway shell

# View environment variables
railway variables

# Check service status
railway status
```

## 📈 **Performance Tips**

### **Optimize Docker Image**
- Use multi-stage builds
- Minimize layers
- Use `.dockerignore`

### **Database Connections**
- Use connection pooling
- Set appropriate timeouts
- Monitor connection usage

### **Caching**
- Enable Redis caching
- Set appropriate TTL
- Monitor cache hit rates

## 🔗 **Useful Links**

- [Railway Documentation](https://docs.railway.app/)
- [Railway CLI](https://docs.railway.app/develop/cli)
- [Railway Pricing](https://railway.app/pricing)
- [Railway Status](https://status.railway.app/)

## 🎉 **Success!**

Once deployed, your MindsDB MCP server will be available at:
`https://your-app-name.railway.app`

You can test it with:
```bash
curl https://your-app-name.railway.app/health
```

Happy deploying! 🚀
