# Custom Branding Module - Docker 18 Setup

## ✅ Module Added to Docker

The `custom_branding` module has been added to your Docker 18 setup.

## What Was Changed

**File:** `docker-compose-odoo18.yml`

Added volume mount:
```yaml
- ./custom_branding:/mnt/extra-addons/custom_branding
```

This mounts your local `custom_branding` module into the Docker container at `/mnt/extra-addons/custom_branding`.

## Configuration

The Odoo 18 config file (`config/odoo18.conf`) already includes:
```
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons,/mnt/extra-addons/enterprise
```

Since `/mnt/extra-addons` is in the addons path, your module will be automatically detected.

## Installation Steps

### 1. Make sure your logo is in place:
```bash
# Place your logo at:
custom_branding/static/img/logo.png
```

### 2. Customize the module (optional):
- Edit `custom_branding/controllers/database.py` line 26: Change "Your Company Name"
- The "Powered by Odoo" text is already removed in templates

### 3. Restart Docker containers:
```bash
cd /Users/abdalla/Desktop/biometric
docker-compose -f docker-compose-odoo18.yml down
docker-compose -f docker-compose-odoo18.yml up -d
```

### 4. Install the module in Odoo:
1. Access Odoo at: `http://localhost:8072`
2. Go to: **Apps** menu
3. Click: **Update Apps List**
4. Search: **"Custom Branding"**
5. Click: **Install**

### 5. Update the module (if already installed):
```bash
# Access Odoo shell or use the UI
# Or restart with update flag:
docker-compose -f docker-compose-odoo18.yml exec web-odoo18 odoo -u custom_branding -d your_database
```

## Verify Installation

After installation, check:
- [ ] Database selection page shows your logo
- [ ] Login page doesn't show "Powered by Odoo"
- [ ] POS receipts don't show "Powered by Odoo"

## Troubleshooting

**Module not showing in Apps?**
- Check Docker logs: `docker-compose -f docker-compose-odoo18.yml logs web-odoo18`
- Verify module path: `docker-compose -f docker-compose-odoo18.yml exec web-odoo18 ls -la /mnt/extra-addons/custom_branding`
- Check for syntax errors in `__manifest__.py`

**Logo not showing?**
- Verify file exists: `docker-compose -f docker-compose-odoo18.yml exec web-odoo18 ls -la /mnt/extra-addons/custom_branding/static/img/`
- Clear browser cache
- Restart container: `docker-compose -f docker-compose-odoo18.yml restart web-odoo18`

**Changes not appearing?**
- Update module: Access Odoo > Apps > Custom Branding > Upgrade
- Or via command: `docker-compose -f docker-compose-odoo18.yml exec web-odoo18 odoo -u custom_branding -d your_database`
- Clear browser cache
- Restart container

## Quick Commands

```bash
# View logs
docker-compose -f docker-compose-odoo18.yml logs -f web-odoo18

# Restart container
docker-compose -f docker-compose-odoo18.yml restart web-odoo18

# Access container shell
docker-compose -f docker-compose-odoo18.yml exec web-odoo18 bash

# Check if module is mounted
docker-compose -f docker-compose-odoo18.yml exec web-odoo18 ls -la /mnt/extra-addons/custom_branding
```

## Notes

- The module is mounted as a volume, so changes to files are reflected immediately (after restart)
- Logo files are served from the mounted volume
- All branding changes are in the `custom_branding` module directory
- No need to rebuild the Docker image


