# Custom Branding Module - Usage Guide

## ✅ Complete UI-Based Branding Management

The module now provides a **Settings interface** where you can manage all branding from the Odoo UI - no code changes needed!

## How to Access Settings

1. **Go to:** Settings (⚙️ icon in top right)
2. **Scroll down to:** "Custom Branding" section
3. **Configure all branding options there**

## Available Settings

### 1. Database Page Logo
- **Field:** Database Page Logo
- **What it does:** Logo shown on database selection page
- **How to set:** Upload image in the settings
- **Format:** PNG or JPG recommended

### 2. Database Page Title
- **Field:** Database Page Title  
- **What it does:** Title shown in browser tab on database page
- **How to set:** Enter text (e.g., "Your Company Name")
- **Default:** "Odoo"

### 3. Login Page "Powered by" Text
- **Field:** Login Page "Powered by" Text
- **What it does:** Text displayed at bottom of login page
- **How to set:** Enter your custom text (e.g., "Powered by Your Company")
- **To hide:** Leave empty
- **URL Field:** Link URL for the text (optional)

### 4. POS Receipt Footer Text
- **Field:** POS Receipt Footer Text
- **What it does:** Text displayed at bottom of POS receipts
- **How to set:** Enter your custom text (e.g., "Powered by Your Company")
- **To hide:** Leave empty

## Step-by-Step Setup

### Step 1: Configure Settings
1. Go to **Settings** (⚙️)
2. Find **"Custom Branding"** section
3. Fill in all fields:
   - Upload database page logo
   - Enter database page title
   - Enter login page "Powered by" text (or leave empty to hide)
   - Enter POS receipt footer text (or leave empty to hide)
4. Click **Save**

### Step 2: Test Changes
- **Database Page:** Visit `/web/database/selector` - should show your logo and title
- **Login Page:** Visit `/web/login` - should show your custom text (or nothing if left empty)
- **POS Receipt:** Print a test receipt - should show your custom footer text (or nothing if left empty)

### Step 3: Company Logo (Separate Setting)
The company logo used in login page and POS is set separately:
- Go to: **Settings > Companies > Your Company**
- Upload logo in the **Logo** field
- This logo appears on:
  - Login page (top)
  - POS login screen
  - POS receipt header

## Features

✅ **All changes via UI** - No code editing needed
✅ **Instant updates** - Changes apply immediately after saving
✅ **Hide options** - Leave fields empty to hide branding text
✅ **Company-specific** - Each company can have different branding
✅ **POS integration** - Works seamlessly with Point of Sale

## Important Notes

- **Database Page Logo:** Must be uploaded via Settings (not file system)
- **Company Logo:** Set separately in Settings > Companies > Logo
- **Empty fields:** Leave text fields empty to hide "Powered by" text
- **Multiple companies:** Each company can have different branding settings

## Troubleshooting

**Changes not appearing?**
1. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
2. Restart Odoo server
3. Update module: Apps > Custom Branding > Upgrade

**Logo not showing?**
- Check file was uploaded successfully
- Clear browser cache
- Check Odoo logs for errors

**POS receipt not updating?**
- Make sure POS session is restarted
- Clear browser cache
- Update module if needed


