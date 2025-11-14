#!/bin/bash
# UH Care PythonAnywhere Deployment Script
# For PythonAnywhere user: authkazee03
# Usage: Copy and paste this entire script into PythonAnywhere Bash console

set -e  # Exit on error

PA_USER=authkazee03
PA_DOMAIN=$PA_USER.pythonanywhere.com
REPO_DIR=~/UnitedHcare-
VENV_PATH=~/venv-uhcare

echo "🚀 Starting UH Care deployment to PythonAnywhere..."
echo "   User: $PA_USER"
echo "   Domain: $PA_DOMAIN"
echo "   Project: $REPO_DIR"
echo ""

# Step 1: Clone repository
echo "📦 Step 1: Cloning GitHub repository..."
cd ~
if [ -d "$REPO_DIR" ]; then
    echo "   Repository already exists, pulling latest changes..."
    cd $REPO_DIR
    git pull origin main
else
    echo "   Cloning from GitHub..."
    git clone https://github.com/aaasaasthaassa-ux/UnitedHcare-.git
    cd $REPO_DIR
fi
echo "   ✓ Repository ready"
echo ""

# Step 2: Create virtualenv
echo "🐍 Step 2: Setting up Python virtualenv..."
if [ -d "$VENV_PATH" ]; then
    echo "   Virtualenv already exists, updating..."
else
    echo "   Creating new virtualenv..."
    python3.11 -m venv $VENV_PATH
fi
source $VENV_PATH/bin/activate
echo "   ✓ Virtualenv activated"
echo ""

# Step 3: Install dependencies
echo "📚 Step 3: Installing Python dependencies..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt
echo "   ✓ Dependencies installed"
echo ""

# Step 4: Django setup
echo "⚙️  Step 4: Running Django setup..."
python manage.py migrate --noinput
echo "   ✓ Database migrations applied"

python manage.py collectstatic --noinput
echo "   ✓ Static files collected"
echo ""

# Step 5: Summary
echo "✅ DEPLOYMENT SETUP COMPLETE!"
echo ""
echo "📝 Next steps (must do manually in PythonAnywhere Web tab):"
echo ""
echo "1️⃣  Set Environment Variables"
echo "   Go to: Web tab → Environment variables → Add these:"
echo ""
echo "   DJANGO_SECRET_KEY = [Generate from: https://miniwebtool.com/django-secret-key-generator/]"
echo "   DJANGO_DEBUG = False"
echo "   DJANGO_ALLOWED_HOSTS = $PA_DOMAIN"
echo ""
echo "   (Optional but recommended:)"
echo "   EMAIL_HOST_USER = your-email@gmail.com"
echo "   EMAIL_HOST_PASSWORD = your-app-specific-gmail-password"
echo ""
echo "2️⃣  Configure WSGI File"
echo "   Go to: Web tab → WSGI configuration file → Edit:"
echo ""
echo "   Replace the entire file content with:"
cat << 'EOF'
import os, sys
path = '/home/authkazee03/UnitedHcare-'
if path not in sys.path:
    sys.path.insert(0, path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
EOF
echo ""
echo ""
echo "3️⃣  Set Virtualenv Path"
echo "   Go to: Web tab → Virtualenv path"
echo "   Enter: /home/authkazee03/venv-uhcare"
echo ""
echo "4️⃣  Configure Static Files"
echo "   Go to: Web tab → Static files"
echo "   Add mapping:"
echo "      URL: /static/"
echo "      Directory: /home/authkazee03/UnitedHcare-/staticfiles"
echo ""
echo "   Add mapping (if using media uploads):"
echo "      URL: /media/"
echo "      Directory: /home/authkazee03/UnitedHcare-/media"
echo ""
echo "5️⃣  Reload Web App"
echo "   Go to: Web tab → Click green 'Reload' button"
echo ""
echo "6️⃣  Visit Your Site"
echo "   Open: https://$PA_DOMAIN"
echo ""
echo "7️⃣  Create Admin User (optional, run this after reload succeeds):"
echo "   python manage.py createsuperuser"
echo "   Then visit: https://$PA_DOMAIN/admin"
echo ""
echo "❓ Troubleshooting:"
echo "   - Check Web tab → Error log if site shows 500 error"
echo "   - Ensure DJANGO_ALLOWED_HOSTS exactly matches your domain"
echo "   - Verify DJANGO_SECRET_KEY is set and non-empty"
echo "   - For static issues, re-run: python manage.py collectstatic --noinput"
echo ""
echo "📞 Need help? See DEPLOY_PYTHONANYWHERE.md in the repo"
echo ""
