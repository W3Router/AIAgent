# Google Cloud Platform 部署指南

## 前置条件

1. Google Cloud 账号
2. 已安装 Google Cloud SDK
3. 项目代码库
4. Docker 和 Docker Compose

## 步骤一：设置 GCP 项目

1. 创建新项目（如果还没有）：
```bash
gcloud projects create [PROJECT_ID] --name="Social Media Automation"
gcloud config set project [PROJECT_ID]
```

2. 启用必要的 API：
```bash
gcloud services enable compute.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

## 步骤二：配置 Container Registry

1. 配置 Docker 认证：
```bash
gcloud auth configure-docker
```

2. 构建并推送 Docker 镜像：
```bash
# 构建镜像
docker build -t gcr.io/[PROJECT_ID]/social-media-automation .

# 推送到 Container Registry
docker push gcr.io/[PROJECT_ID]/social-media-automation
```

## 步骤三：创建计算引擎实例

1. 创建 VM 实例：
```bash
gcloud compute instances create social-media-automation \
    --machine-type=e2-medium \
    --zone=asia-east1-a \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=20GB \
    --tags=http-server,https-server
```

2. 配置防火墙规则：
```bash
# 允许 HTTP 流量
gcloud compute firewall-rules create allow-http \
    --allow tcp:80 \
    --target-tags=http-server

# 允许 HTTPS 流量
gcloud compute firewall-rules create allow-https \
    --allow tcp:443 \
    --target-tags=https-server

# 允许应用端口
gcloud compute firewall-rules create allow-app \
    --allow tcp:8000 \
    --target-tags=http-server
```

## 步骤四：配置实例

1. SSH 连接到实例：
```bash
gcloud compute ssh social-media-automation
```

2. 安装 Docker 和 Docker Compose：
```bash
# 更新包列表
sudo apt-get update

# 安装必要的包
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 添加 Docker 的官方 GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 设置稳定版仓库
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER
```

## 步骤五：部署应用

1. 克隆代码库：
```bash
git clone [YOUR_REPOSITORY_URL]
cd social-media-automation
```

2. 配置环境变量：
```bash
cp .env.example .env
nano .env  # 编辑配置文件
```

3. 启动应用：
```bash
docker-compose up -d
```

## 步骤六：配置域名和 SSL（可选）

1. 在 GCP 控制台中配置静态 IP：
```bash
gcloud compute addresses create social-media-automation-ip --region=asia-east1
```

2. 获取分配的 IP：
```bash
gcloud compute addresses describe social-media-automation-ip --region=asia-east1
```

3. 配置域名 DNS A 记录指向此 IP

4. 安装 Certbot 并获取 SSL 证书：
```bash
sudo snap install --classic certbot
sudo certbot certonly --standalone -d your-domain.com
```

## 监控和维护

1. 查看容器日志：
```bash
docker-compose logs -f
```

2. 监控资源使用：
```bash
# 访问 Grafana
http://[YOUR_IP]:3000

# 访问 Prometheus
http://[YOUR_IP]:9090
```

3. 更新应用：
```bash
# 拉取最新代码
git pull

# 重建容器
docker-compose down
docker-compose up -d --build
```

## 成本优化

1. 使用预留实例可以节省成本
2. 设置资源配额限制
3. 监控并优化资源使用

## 故障排除

1. 检查实例状态：
```bash
gcloud compute instances describe social-media-automation
```

2. 检查容器状态：
```bash
docker-compose ps
```

3. 查看应用日志：
```bash
docker-compose logs social_media_automation
```

## 安全建议

1. 使用 IAM 角色和服务账号
2. 定期更新系统和依赖
3. 启用 Cloud Audit Logs
4. 配置网络安全组
5. 使用密钥管理服务存储敏感信息

## 备份策略

1. 配置自动备份：
```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
tar -czf $BACKUP_DIR/backup_$TIMESTAMP.tar.gz data/ .env
gsutil cp $BACKUP_DIR/backup_$TIMESTAMP.tar.gz gs://[YOUR_BUCKET]/backups/
EOF

# 添加执行权限
chmod +x backup.sh

# 添加到 crontab
echo "0 0 * * * /path/to/backup.sh" | crontab -
```

## 扩展建议

1. 设置负载均衡器
2. 配置自动扩展
3. 使用 Cloud CDN
4. 实施日志聚合
5. 配置告警通知
