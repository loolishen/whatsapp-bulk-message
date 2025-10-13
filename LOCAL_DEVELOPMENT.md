# Local Development Setup

This guide explains how to run the WhatsApp Bulk Message application locally for development without interfering with your GCP deployment.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Windows
run_local.bat

# Linux/Mac
chmod +x run_local.sh
./run_local.sh

# Or directly with Python
python run_local.py
```

### Option 2: Manual Setup
```bash
# 1. Run migrations
python manage_local.py migrate

# 2. Create superuser (optional)
python manage_local.py createsuperuser

# 3. Start development server
python manage_local.py runserver
```

## 📁 Files Created for Local Development

- `whatsapp_bulk/settings_local.py` - Local development settings using SQLite
- `manage_local.py` - Django management script for local development
- `run_local.py` - Automated setup and server runner
- `run_local.bat` - Windows batch file for easy startup
- `run_local.sh` - Unix/Linux/Mac shell script

## 🔧 Local Development Features

### Database
- **Local**: Uses SQLite (`db.sqlite3`) - completely separate from GCP
- **Production**: Uses PostgreSQL on Google Cloud SQL
- **No Conflicts**: Local development won't interfere with production data

### Settings Differences
| Setting | Local Development | Production |
|---------|-------------------|-----------|
| Database | SQLite | PostgreSQL |
| Debug | True | False |
| HTTPS | Disabled | Enabled |
| Secret Key | Development key | Environment variable |
| Allowed Hosts | localhost, 127.0.0.1 | Production domains |

### API Configuration
- Uses the same API keys as production (safe for development)
- Cloudinary folder is set to `whatsapp_bulk_local` to avoid conflicts
- WhatsApp API uses test instance

## 🌐 Access Points

When running locally, you can access:

- **Main Application**: http://127.0.0.1:8000
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Default Login**: admin / admin123 (if using automated setup)

## 🛠️ Development Workflow

1. **Make Changes**: Edit your code locally
2. **Test Locally**: Use `python run_local.py` or `run_local.bat`
3. **Deploy to GCP**: When ready, deploy using your existing GCP deployment process

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Use a different port
   python manage_local.py runserver 8001
   ```

2. **Database Issues**
   ```bash
   # Reset the local database
   rm db.sqlite3
   python manage_local.py migrate
   ```

3. **Permission Issues (Linux/Mac)**
   ```bash
   chmod +x run_local.sh
   chmod +x run_local.py
   ```

### Debug Mode
The local development server runs with `DEBUG=True`, so you'll see detailed error pages and Django's debug toolbar.

## 📝 Notes

- Local development uses SQLite, so it's fast and doesn't require database setup
- All your local changes are isolated from production
- You can safely experiment without affecting your GCP deployment
- The automated setup creates a default admin user for easy testing

## 🚀 Next Steps

1. Run the local development server
2. Test your WhatsApp preview changes
3. Make any necessary adjustments
4. Deploy to GCP when ready

Happy coding! 🎉
