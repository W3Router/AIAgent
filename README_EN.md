# Social Media Automation System with Email Review

A powerful social media automation system that integrates ChatGPT, Twitter API, and TweetHunter, featuring email-based content review.

## Key Features

- AI-powered content generation using ChatGPT
- Email-based content review system
- One-click review actions (approve/reject/edit)
- 24-hour auto-approval mechanism
- Automated content publishing
- Intelligent scheduling system
- Cross-platform support

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
- Copy `.env.example` to `.env`
- Fill in all required API keys and email settings

## Email Configuration

The system uses SMTP for sending review emails and supports major email providers:

### For Gmail Users:
1. Enable 2-Factor Authentication
2. Generate an App Password
3. Use the App Password in `.env`

### Required Email Settings in `.env`:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
REVIEWER_EMAIL=reviewer@example.com
```

## Usage Guide

1. Start the API server:
```bash
python api_server.py
```

2. Launch the automation system:
```bash
python social_media_automation.py
```

The system will automatically:
- Generate content at 9:00, 15:00, and 20:00 daily
- Send review emails to the specified address
- Wait for review or auto-approve after 24 hours
- Publish approved content at the next hour mark

## Review Process

1. **Receive Review Email**
   - Check your inbox for review notifications
   - Review emails contain the content preview and action buttons

2. **Review Options**
   - Green Button: Approve for publishing
   - Red Button: Reject content
   - Blue Button: Edit content

3. **Auto-Approval System**
   - Content will be automatically approved if not reviewed within 24 hours
   - System logs auto-approved content for tracking
   - Auto-approved content is published at the next scheduled time

## Best Practices

1. **Content Review**
   - Review content promptly when possible
   - Check spam folder regularly
   - Make decisions within 24 hours if auto-approval is not desired

2. **Security**
   - Keep your JWT secret key secure
   - Don't share review email links
   - Update email passwords regularly

3. **Monitoring**
   - Check system logs regularly
   - Monitor auto-approved content
   - Review publishing patterns and adjust scheduling if needed

## Troubleshooting

1. **Email Issues**
   - Verify SMTP settings
   - Check spam folders
   - Ensure email server ports are accessible

2. **Publishing Issues**
   - Verify API credentials
   - Check internet connectivity
   - Review system logs for errors

3. **Content Generation Issues**
   - Verify OpenAI API key
   - Check API rate limits
   - Monitor ChatGPT response quality

## API Key Setup

1. **OpenAI API Key**
   - Visit: https://platform.openai.com/
   - Create an account and generate API key
   - Add key to `.env` file

2. **Twitter API Keys**
   - Visit: https://developer.twitter.com/
   - Create a developer account
   - Apply for API access
   - Generate required keys and tokens

3. **TweetHunter API Key**
   - Subscribe to TweetHunter Pro
   - Access API key from settings
   - Add to `.env` file

## Important Notes

1. **System Requirements**
   - Python 3.8 or higher
   - Stable internet connection
   - Access to SMTP ports

2. **Rate Limits**
   - Respect Twitter API rate limits
   - Monitor OpenAI API usage
   - Check email sending limits

3. **Content Guidelines**
   - Review auto-generated content quality
   - Ensure compliance with platform policies
   - Monitor audience engagement

4. **Maintenance**
   - Regularly update dependencies
   - Monitor system logs
   - Backup database periodically

## Support

For issues or assistance:
- Submit an issue on GitHub
- Contact support team
- Check documentation updates

## License

[Specify your license here]

---

Note: This system is designed for automation while maintaining content quality through human oversight. The 24-hour auto-approval feature ensures content flow while allowing for manual review when possible.
