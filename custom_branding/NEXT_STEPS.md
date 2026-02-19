# Next Steps After Installation ✅

Great! The module is installed. Now let's complete the branding setup:

## Step 1: Add Your Logo for Database Page

1. **Place your logo file:**
   ```
   custom_branding/static/img/logo.png
   ```
   - Format: PNG (recommended) or JPG
   - Size: Similar to original (check `V18-enterprise/web/static/img/logo2.png` dimensions)

2. **After adding the logo, restart Docker:**
   ```bash
   docker-compose -f docker-compose-odoo18.yml restart web-odoo18
   ```

## Step 2: Customize Database Page Title

1. **Edit:** `custom_branding/controllers/database.py`
2. **Line 26:** Change `"Your Company Name"` to your actual company name
3. **Restart Docker** after making changes

## Step 3: Set Company Logo (Login & POS)

The company logo appears on:
- Login page
- POS login screen  
- POS receipt header

**To set it:**
1. Go to: **Settings > Companies > Your Company**
2. Click **Edit**
3. Upload your logo in the **Logo** field
4. Click **Save**

## Step 4: Verify Everything Works

Check these locations:

- [ ] **Database Selection Page** (`http://localhost:8072/web/database/selector`)
  - Should show your logo instead of Odoo logo
  - Title should be your company name (if customized)

- [ ] **Login Page** (`http://localhost:8072/web/login`)
  - Should NOT show "Powered by Odoo" at bottom
  - Should show your company logo (if set in Step 3)

- [ ] **POS Receipt** (Print a test receipt)
  - Should NOT show "Powered by Odoo" at bottom
  - Should show your company logo in header (if set in Step 3)

## Step 5: Clear Browser Cache (If Changes Don't Appear)

If you don't see changes:
1. **Hard refresh:** `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
2. **Or clear cache:** Browser Settings > Clear Browsing Data > Cached images and files

## Quick Commands

```bash
# Restart Docker after logo changes
docker-compose -f docker-compose-odoo18.yml restart web-odoo18

# View logs if issues
docker-compose -f docker-compose-odoo18.yml logs -f web-odoo18

# Update module if needed
docker-compose -f docker-compose-odoo18.yml exec web-odoo18 odoo -u custom_branding -d your_database
```

## Current Status

✅ Module installed
✅ "Powered by Odoo" removed from login page
✅ "Powered by Odoo" removed from POS receipts
⏳ **Next:** Add your logo and customize company name

## Troubleshooting

**Logo not showing on database page?**
- Check file exists: `custom_branding/static/img/logo.png`
- Restart Docker container
- Clear browser cache

**Company logo not showing?**
- Make sure you uploaded it via Settings > Companies > Logo
- Clear browser cache

**Changes not appearing?**
- Restart Docker: `docker-compose -f docker-compose-odoo18.yml restart web-odoo18`
- Clear browser cache
- Hard refresh page


