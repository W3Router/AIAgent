# 部署指南

本文档介绍如何将社交媒体自动化系统部署到云服务器。

## 系统要求

- Docker
- Docker Compose
- 2GB+ RAM
- 20GB+ 存储空间
- 稳定的网络连接

## 部署步骤

### 1. 准备服务器

选择一个云服务提供商并创建服务器实例：

#### AWS EC2
```bash
# 安装 Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Ubuntu/Debian
```bash
# 安装 Docker
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 配置项目

1. 克隆项目到服务器：
```bash
git clone [your-repository-url]
cd social-media-automation
```

2. 创建并配置环境变量：
```bash
cp .env.example .env
nano .env  # 编辑配置文件
```

需要配置的重要变量：
- Twitter API 密钥
- OpenAI API 密钥
- SMTP 邮件服务器设置
- Zapier Webhook URLs（可选）

### 3. 启动服务

```bash
# 构建并启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 4. 配置域名和SSL（推荐）

1. 配置域名 A 记录指向服务器 IP

2. 使用 Certbot 配置 SSL：
```bash
sudo apt-get install certbot
sudo certbot certonly --standalone -d your-domain.com
```

3. 更新 nginx 配置（如果使用）

### 5. 监控

访问以下地址查看系统状态：
- Grafana: http://your-domain:3000
- Prometheus: http://your-domain:9090

### 6. 维护

#### 更新系统
```bash
git pull
docker-compose down
docker-compose up -d --build
```

#### 备份数据
```bash
# 备份数据库和配置
tar -czf backup.tar.gz data/ .env
```

#### 查看日志
```bash
docker-compose logs -f social_media_automation
```

## 安全建议

1. 配置防火墙，只开放必要端口
2. 使用强密码
3. 定期更新系统和依赖
4. 启用 SSL/TLS
5. 定期备份数据

## 故障排除

1. 容器无法启动
```bash
docker-compose logs social_media_automation
```

2. API 连接问题
- 检查 .env 配置
- 验证 API 密钥
- 检查网络连接

3. 邮件发送问题
- 验证 SMTP 设置
- 检查邮件服务器日志

## 监控指标

- CPU 使用率
- 内存使用
- 磁盘空间
- API 调用频率
- 发布成功率
- 响应时间

## 联系支持

如遇到问题，请：
1. 查看日志文件
2. 检查配置
3. 联系技术支持
