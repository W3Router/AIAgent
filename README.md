# 社交媒体自动化系统（邮件审核版）

这是一个强大的社交媒体自动化系统，集成了ChatGPT、Twitter API和TweetHunter，并通过邮件进行内容审核。

## 功能特点

- 使用ChatGPT自动生成个性化内容
- 通过邮件进行内容审核
- 支持一键式审核（批准/拒绝/编辑）
- 24小时自动发布机制
- 自动发布已审核内容
- 智能调度系统确保最佳发布时间

## 安装步骤

1. 克隆仓库：
```bash
git clone [repository-url]
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
- 复制 `.env.example` 到 `.env`
- 填写所有必要的API密钥和邮件配置

## 邮件配置说明

系统使用SMTP发送审核邮件，支持主流邮件服务商：

- Gmail
- Outlook
- 其他SMTP服务器

对于Gmail用户：
1. 开启两步验证
2. 生成应用专用密码
3. 在.env中使用应用专用密码

## 使用方法

1. 启动API服务器：
```bash
python api_server.py
```

2. 启动自动化系统：
```bash
python social_media_automation.py
```

系统将自动：
- 每天在9:00、15:00和20:00生成内容
- 发送审核邮件给指定邮箱
- 等待通过邮件进行审核
- 在审核通过后的下一个整点发布内容

## 审核流程

1. 收到审核邮件
2. 查看待发布内容
3. 点击邮件中的按钮：
   - 绿色按钮：批准发布
   - 红色按钮：拒绝发布
   - 蓝色按钮：编辑内容
4. 自动发布机制：
   - 如果内容在24小时内未被审核
   - 系统将自动批准并发布
   - 发布时会记录自动审核日志

## API密钥获取方法

1. OpenAI API密钥：
   - 访问 https://platform.openai.com/
   - 注册并创建API密钥

2. Twitter API密钥：
   - 访问 https://developer.twitter.com/
   - 创建开发者账户并申请API访问权限

3. TweetHunter API密钥：
   - 访问 TweetHunter官网
   - 注册专业版账户
   - 在设置中获取API密钥

## 注意事项

- 确保邮件服务器配置正确
- 定期检查垃圾邮件文件夹
- 保护好JWT密钥的安全
- 及时处理审核邮件，避免内容积压
- 确保服务器能够访问邮件服务器的SMTP端口

## 支持

如有问题或需要帮助，请提交Issue或联系支持团队。

## 内容管理系统（Content Management System）

这是一个强大的内容管理系统，集成了 OpenAI、Twitter API 和邮件审核功能，支持内容生成、编辑和发布。

## 功能特点

- 使用 OpenAI 自动生成内容
- 通过网页界面编辑和优化内容
- AI 辅助内容改进
- 邮件通知和审核系统
- 支持一键式审核（批准/拒绝/重新生成）
- 自动发布到 Twitter

## 部署指南

### 1. 环境要求

- Docker 和 Docker Compose
- 可访问的 SMTP 服务器
- OpenAI API 密钥
- Twitter API 凭证

### 2. 配置步骤

1. 克隆仓库：
```bash
git clone [repository-url]
cd [repository-name]
```

2. 配置环境变量：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填写以下配置：
```
# OpenAI 配置
OPENAI_API_KEY=your_openai_api_key

# Twitter API 配置
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# SMTP 配置
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_specific_password
REVIEWER_EMAIL=reviewer@example.com

# 应用配置
BASE_URL=https://your-domain.com  # 生产环境 URL
```

### 3. 使用 Docker Compose 部署

1. 启动所有服务：
```bash
docker-compose up -d
```

2. 检查服务状态：
```bash
docker-compose ps
```

3. 查看日志：
```bash
docker-compose logs -f
```

### 4. 访问系统

- Web 界面：http://your-domain.com:5001
- Grafana 监控：http://your-domain.com:3000
- Prometheus 指标：http://your-domain.com:9090

## 使用说明

1. **生成内容**：
   - 选择选项 1
   - 输入想要的主题
   - 系统会使用 OpenAI 生成相关内容

2. **直接输入内容**：
   - 选择选项 2
   - 直接输入想要发布的内容
   - 输入完成后按两次 Enter
   - 预览内容并确认

3. **内容审核流程**：
   - 收到审核邮件后，点击"Review & Edit Content"
   - 在网页界面上编辑内容
   - 可以提供反馈让 AI 重新生成
   - 确认满意后点击"Approve & Post"

## 安全建议

1. **API 密钥保护**：
   - 使用环境变量存储所有敏感信息
   - 不要在代码中硬编码任何密钥
   - 定期轮换 API 密钥

2. **邮件安全**：
   - 对于 Gmail，使用应用专用密码
   - 启用 SMTP TLS 加密
   - 定期更新邮件密码

3. **网络安全**：
   - 在生产环境中使用 HTTPS
   - 配置适当的防火墙规则
   - 限制必要的端口访问

## 监控和维护

系统集成了 Prometheus 和 Grafana 用于监控：

- 系统性能指标
- API 调用统计
- 错误率监控
- 响应时间追踪

## 故障排除

常见问题及解决方案：

1. **邮件发送失败**：
   - 检查 SMTP 配置
   - 确认网络连接
   - 验证邮箱凭证

2. **API 调用错误**：
   - 检查 API 密钥有效性
   - 确认 API 使用配额
   - 查看错误日志

3. **容器启动问题**：
   - 检查 Docker 日志
   - 验证环境变量
   - 确认端口可用性

## 贡献指南

欢迎提交 Pull Requests！请确保：

1. 遵循现有代码风格
2. 添加适当的测试
3. 更新相关文档

## 许可证

[您的许可证类型]

## GCP 部署指南

### 1. 前置要求

- Google Cloud Platform 账号
- 已安装并配置 [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- 启用以下 GCP 服务：
  - Cloud Run
  - Cloud Build
  - Container Registry
  - Secret Manager

### 2. 配置 GCP 项目

1. 设置项目和区域：
```bash
# 设置项目 ID
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# 设置区域
gcloud config set run/region asia-east1
```

2. 创建密钥：
```bash
# 创建密钥
echo -n "your-openai-api-key" | gcloud secrets create openai-api-key --data-file=-
echo -n "your-twitter-api-key" | gcloud secrets create twitter-api-key --data-file=-
echo -n "your-twitter-api-secret" | gcloud secrets create twitter-api-secret --data-file=-
echo -n "your-twitter-access-token" | gcloud secrets create twitter-access-token --data-file=-
echo -n "your-twitter-access-token-secret" | gcloud secrets create twitter-access-token-secret --data-file=-
echo -n "your-twitter-bearer-token" | gcloud secrets create twitter-bearer-token --data-file=-
echo -n "your-smtp-password" | gcloud secrets create smtp-password --data-file=-
```

3. 授予权限：
```bash
# 授予 Cloud Run 访问密钥的权限
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 3. 部署应用

1. 提交代码到 Cloud Source Repository：
```bash
# 初始化仓库
gcloud source repos create content-management
git init
git remote add google "https://source.developers.google.com/p/$PROJECT_ID/r/content-management"

# 提交代码
git add .
git commit -m "Initial commit"
git push google master
```

2. 触发构建和部署：
```bash
gcloud builds submit --config=cloudbuild.yaml
```

3. 验证部署：
```bash
# 查看 Web 服务状态
gcloud run services describe content-web --platform managed --region asia-east1

# 查看 Assistant 服务状态
gcloud run services describe content-assistant --platform managed --region asia-east1
```

### 4. 配置域名（可选）

1. 映射自定义域名：
```bash
gcloud beta run domain-mappings create \
    --service content-web \
    --domain your-domain.com \
    --platform managed \
    --region asia-east1
```

2. 更新 DNS 记录：
按照 Cloud Run 提供的说明更新您的 DNS 记录。

### 5. 监控和日志

1. 查看日志：
```bash
# Web 服务日志
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=content-web" --limit 50

# Assistant 服务日志
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=content-assistant" --limit 50
```

2. 监控指标：
- 访问 Cloud Console > Cloud Run > 服务
- 查看每个服务的指标：
  - 请求数
  - 延迟
  - 内存使用
  - CPU 使用

### 6. 成本优化

Cloud Run 采用按使用量付费模式：
- 仅在处理请求时收费
- 自动扩缩容
- 空闲时不收费

成本优化建议：
1. 设置适当的内存限制（当前设置为 512Mi）
2. 监控并优化请求处理时间
3. 使用 Cloud Run 的自动扩缩容功能

### 7. 故障排除

常见问题及解决方案：

1. **部署失败**：
   - 检查 Cloud Build 日志
   - 验证服务账号权限
   - 确认密钥配置正确

2. **服务无法访问**：
   - 检查防火墙规则
   - 验证域名配置
   - 查看服务日志

3. **性能问题**：
   - 调整内存配置
   - 检查代码效率
   - 监控资源使用
