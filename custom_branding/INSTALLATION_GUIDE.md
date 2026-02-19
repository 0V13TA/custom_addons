# Custom Branding Module - Quick Installation Guide

## ✅ YES, it's possible to remove all Odoo logos and use your branding!

This module has been created to help you completely rebrand Odoo 18 Enterprise.

## What This Module Does

✅ **Removes "Powered by Odoo" from:**
- Login page
- POS receipts
- Footer brand promotion

✅ **Replaces:**
- Database manager page logo
- Database manager page title

✅ **Uses your company logo:**
- Login page (via Settings > Companies > Logo)
- POS login screen (via Settings > Companies > Logo)
- POS receipt header (via Settings > Companies > Logo)

## Quick Start (3 Steps)

### Step 1: Add Your Logo
1. Place your logo file at: `custom_branding/static/img/logo.png`
2. Recommended: PNG format, similar size to original logo

### Step 2: Customize Text
1. Edit `controllers/database.py`:
   - Line 26: Change "Your Company Name" to your actual company name

2. Edit `views/templates.xml`:
   - Lines 8-9: Currently removes "Powered by Odoo" (you can customize if needed)
   - Lines 20-21: Currently removes "Powered by Odoo" from POS receipts

### Step 3: Install
1. Restart Odoo server
2. Go to: **Apps > Update Apps List**
3. Search: **"Custom Branding"**
4. Click: **Install**

## What Gets Changed

| Location | What Changes | How to Customize |
|----------|-------------|------------------|
| **Database Page** | Logo & Title | `controllers/database.py` + `static/img/logo.png` |
| **Login Page** | "Powered by Odoo" removed | Already done in `templates.xml` |
| **POS Receipt** | "Powered by Odoo" removed | Already done in `templates.xml` |
| **Company Logo** | Your logo everywhere | Settings > Companies > Logo (UI) |

## After Installation

1. **Clear browser cache** (Ctrl+Shift+Delete or Cmd+Shift+Delete)
2. **Test:**
   - Visit database selection page → Should see your logo
   - Login page → No "Powered by Odoo"
   - Print POS receipt → No "Powered by Odoo"

## Important Notes

- ✅ **Safe for updates:** Uses template inheritance, won't break on Odoo updates
- ✅ **Reversible:** Uninstall module to restore original branding
- ✅ **No core files modified:** All changes are in this module

## Troubleshooting

**Logo not showing?**
- Check file exists: `custom_branding/static/img/logo.png`
- Clear browser cache
- Restart Odoo server
- Check Odoo logs for errors

**Changes not appearing?**
- Make sure module is installed and active
- Update module: `odoo-bin -u custom_branding -d your_database`
- Clear browser cache
- Restart Odoo server

## Need Help?

Check the detailed `README.md` file for more information.


