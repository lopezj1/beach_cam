# Beach Cam Object Detection Monitor

A serverless beach cam monitoring system that automatically detects cars and people in live video streams and sends email alerts when thresholds are exceeded.

## 🎯 Features

- **Scheduled Processing**: Runs every 30 minutes via GitHub Actions
- **Object Detection**: YOLOv8 detects cars and people
- **Smart Alerts**: Email notifications with detection images when 3+ objects detected
- **Cloud Storage**: Videos stored in Cloudflare R2 with automatic 24-hour cleanup
- **Zero Cost**: Completely free operation with GitHub Actions and Cloudflare free tiers
- **No Frontend**: Headless monitoring service

## 🏗️ Architecture

```
GitHub Actions (every 30 min)
    ↓
Download 5-min video segment
    ↓
YOLO object detection (cars + people)
    ↓
Upload to Cloudflare R2
    ↓
Send email alert if 3+ objects detected
    ↓
Cloudflare auto-cleanup (24-hour lifecycle)
```

## 🚀 Quick Start

### 1. Repository Setup
```bash
# Clone repository
git clone https://github.com/yourusername/beach-cam.git
cd beach-cam

# Install dependencies locally (for testing)
pip install -r requirements.txt
```

### 2. Cloudflare R2 Setup

#### Option A: Dashboard Setup (Recommended)
1. Create R2 bucket: `beach-cam-videos`
2. Add lifecycle rule:
   - **Name**: 24-hour video cleanup
   - **Prefix**: `beach-cam-`
   - **Expiration**: 1 day
   - **Action**: Delete
3. Generate API token with Object Read & Write permissions

#### Option B: CLI Setup
```bash
# Install Wrangler
npm install -g wrangler

# Create bucket and apply lifecycle rule
wrangler r2 bucket create beach-cam-videos
wrangler r2 bucket lifecycle add beach-cam-videos \
  --prefix "beach-cam-" \
  --expiration "1 day" \
  --action "delete"
```

### 3. GitHub Repository Configuration

#### Required Secrets
Add these secrets to your GitHub repository settings:

```
R2_ACCOUNT_ID=your_cloudflare_account_id
R2_ACCESS_KEY=your_r2_access_key_id
R2_SECRET_KEY=your_r2_secret_access_key
R2_BUCKET=beach-cam-videos

EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
RECIPIENT_EMAIL=alerts@example.com
```

#### Gmail App Password Setup
1. Enable 2FA on your Gmail account
2. Go to Google Account → Security → 2-Step Verification → App passwords
3. Create new app password for "Beach Cam"
4. Use the 16-character password in repository secrets

### 4. Enable Workflow
1. Push to main branch
2. Go to Actions tab in GitHub
3. Enable "Beach Cam Video Processor" workflow
4. Test with "Run workflow" button

## 📁 File Structure

```
beach_cam/
├── .github/workflows/
│   └── video-processor.yml     # GitHub Actions workflow
├── src/
│   ├── __init__.py
│   ├── main.py                 # Main orchestration
│   ├── video_processor.py       # yt-dlp video handling
│   ├── detector.py             # YOLO object detection
│   ├── storage_manager.py       # Cloudflare R2 upload
│   └── config.py              # Configuration
├── lifecycle-rule.json          # Optional R2 lifecycle rule
├── requirements.txt             # Python dependencies
└── README.md                  # This file
```

## ⚙️ Configuration

### Detection Settings
- **Classes**: Person (0), Car (2)
- **Threshold**: 3+ objects triggers alert
- **Confidence**: 50% minimum
- **Video Quality**: Optimized for storage (720p max)

### Email Notifications
- **Provider**: Any SMTP server (Gmail recommended)
- **Format**: HTML email with detection image attached
- **Content**: Object count, timestamp, video link
- **Frequency**: Only when threshold exceeded

### Storage Settings
- **Retention**: 24 hours (automatic via Cloudflare lifecycle)
- **Naming**: `beach-cam-YYYY-MM-DD-HH-MM-SS.mp4`
- **Location**: Cloudflare global CDN

## 🔧 Local Development

### Testing the System
```bash
# Run locally (requires environment variables)
export R2_ACCOUNT_ID="your_id"
export R2_ACCESS_KEY="your_key"
export R2_SECRET_KEY="your_secret"
export R2_BUCKET="test-bucket"
export EMAIL_USERNAME="test@example.com"
# ... set all env vars

python -m src.main
```

### Dependencies
```txt
numpy==2.1.0                    # Numerical operations
opencv_python==4.10.0.84         # Computer vision
requests==2.32.3                   # HTTP requests
yt_dlp==2024.8.6                  # YouTube downloading
ultralytics==8.3.0                 # YOLO model
boto3==1.34.0                      # Cloudflare R2 (S3-compatible)
python-dotenv==1.0.0                 # Environment management
```

## 📊 Monitoring

### GitHub Actions Logs
Monitor execution in Actions tab → workflow runs

### Cloudflare Dashboard
Check storage usage, uploaded files, and lifecycle management

### Email Delivery
Verify email notifications are being received

### Performance Metrics
- Video processing time
- Detection counts per run
- Email delivery success rate
- Storage usage trends

## 🔒 Security

### Secrets Management
- All sensitive data in GitHub repository secrets
- No hardcoded credentials in code
- Environment-based configuration

### Best Practices
- Use app passwords for email accounts
- Regularly rotate API tokens
- Monitor usage quotas
- Keep dependencies updated

## 🚨 Troubleshooting

### Common Issues

**Workflow Not Running**
- Verify cron syntax in workflow file
- Check repository has recent activity
- Ensure Actions tab shows workflow enabled

**Email Not Sending**
- Verify SMTP credentials are correct
- Check email app password (not regular password)
- Confirm recipient email address

**R2 Upload Failing**
- Validate bucket permissions
- Check account ID and access keys
- Verify bucket name matches

**Detection Not Working**
- Confirm YOLO model file exists
- Check video download success
- Verify confidence threshold

### Debug Mode
Set detection threshold to 0 for testing to receive alerts on every run.

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make your changes
4. Test thoroughly
5. Submit pull request

---

**Enjoy your automated beach cam monitoring! 🏖️**