# Splunk Dashboard Automator - Desktop Application

## Overview

This is the desktop version of the Splunk Dashboard Automator, converted from the web application to a native desktop GUI using Python's tkinter library.

## Features

- **Native Desktop Interface**: Clean, professional GUI with tabbed interface
- **Credential Management**: Secure encrypted storage of Splunk credentials
- **Dashboard Management**: Add, edit, delete, and organize dashboards
- **List Management**: Group dashboards into organized lists
- **Screenshot Capture**: Automated screenshot capture of Splunk dashboards
- **Settings Management**: Configurable timeouts, directories, and preferences
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation & Setup

### Prerequisites

1. **Python 3.7 or higher** - Download from [python.org](https://python.org)
2. **Git** (optional) - For cloning the repository

### Step 1: Download the Application

Option A: Download the files directly from this Replit
Option B: Clone the repository (if available)

### Step 2: Install Dependencies

Open Command Prompt or PowerShell and navigate to the application directory:

```bash
cd path/to/splunk-dashboard-automator
```

Install the required Python packages:

```bash
pip install flask playwright cryptography pillow pytz tkcalendar
```

Install Playwright browser for screenshot functionality:

```bash
playwright install chromium
```

### Step 3: Run the Application

```bash
python simple_desktop_app.py
```

## Application Structure

```
splunk-dashboard-automator/
├── simple_desktop_app.py      # Main desktop application
├── utils/
│   ├── config.py              # Configuration settings
│   ├── encryption.py          # Credential encryption
│   ├── screenshot.py          # Screenshot capture logic
│   ├── scheduler.py           # Task scheduling
│   └── dashboard_manager.py   # Dashboard management
├── dashboards.json            # Dashboard storage (created automatically)
├── lists.json                 # List storage (created automatically)
├── .secrets                   # Encrypted credentials (created automatically)
├── .secrets.key              # Encryption key (created automatically)
├── logs/                     # Application logs
├── screenshots/              # Screenshot storage
└── tmp/                      # Temporary files
```

## Using the Application

### 1. Credentials Tab

- Enter your Splunk username and password
- Click "Save Credentials" to securely store them
- Credentials are encrypted using Fernet encryption

### 2. Dashboards Tab

- Add new dashboards with name and URL
- Assign dashboards to lists for organization
- Take screenshots of individual dashboards
- Delete or manage existing dashboards

### 3. Lists Tab

- Create new lists to organize your dashboards
- Add descriptions to lists
- View dashboard count per list
- Delete lists when no longer needed

### 4. Settings Tab

- Configure screenshot timeout settings
- Set maximum concurrent screenshots
- Change screenshot storage directory
- Adjust other application preferences

## Features Comparison: Desktop vs Web

| Feature | Desktop App | Web App |
|---------|-------------|---------|
| User Interface | Native tkinter GUI | Modern Bootstrap web UI |
| Accessibility | Local desktop only | Network accessible |
| Performance | Direct system access | Network dependent |
| Security | Local file storage | Session-based |
| Deployment | Single executable | Web server required |
| Multi-user | Single user | Multi-user capable |

## Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named..."**
   - Install missing packages: `pip install [package-name]`

2. **Screenshot capture fails**
   - Install Playwright browsers: `playwright install chromium`
   - Check internet connection
   - Verify Splunk credentials

3. **Permission errors on Windows**
   - Run Command Prompt as Administrator
   - Check antivirus software blocking Python

4. **Application won't start**
   - Verify Python 3.7+ is installed: `python --version`
   - Check all dependencies are installed
   - Review error messages in console

### Error Logs

Application logs are stored in the `logs/` directory:
- `app.log` - General application logs
- Check these files for detailed error information

## Security Notes

- Credentials are encrypted using industry-standard Fernet encryption
- Encryption keys are stored locally in `.secrets.key`
- Never share `.secrets` or `.secrets.key` files
- Use strong, unique passwords for your Splunk accounts

## Advanced Configuration

### Custom Screenshot Directory

Change the screenshot storage location in Settings tab or modify:
```python
Config.SCREENSHOT_ARCHIVE_DIR = "your/custom/path"
```

### Network Configuration

For corporate networks, you may need to:
- Configure proxy settings
- Whitelist Python/Playwright in firewall
- Install certificates if using self-signed SSL

## Development

### Running in Development Mode

For development, you can modify the source code and run:

```bash
python simple_desktop_app.py
```

### Adding New Features

The application is modular:
- GUI logic: `simple_desktop_app.py`
- Business logic: `utils/` modules
- Configuration: `utils/config.py`

## Support

For issues specific to your environment:
1. Check the troubleshooting section
2. Review application logs
3. Verify all dependencies are installed
4. Test with a simple Splunk dashboard first

## License

This application is provided as-is for educational and business use.