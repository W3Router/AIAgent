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
