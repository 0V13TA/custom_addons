# Custom Branding Module

This module removes all Odoo branding and replaces it with your custom branding.

## Features

- ✅ Removes "Powered by Odoo" from login page
- ✅ Removes "Powered by Odoo" from POS receipts
- ✅ Replaces database manager page logo
- ✅ Changes database manager page title
- ✅ Removes brand promotion from footer (if used)

## Installation

1. **Place your logo file:**
   - Copy your logo to: `custom_branding/static/img/logo.png`
   - Recommended format: PNG
   - Recommended size: Similar to original (check dimensions of `V18-enterprise/web/static/img/logo2.png`)

2. **Customize the templates:**
   - Edit `views/templates.xml` to:
     - Change "Your Company Name" to your actual company name (line 7)
     - Update logo path if using different filename (line 11)
     - Customize or remove "Powered by" text (lines 20-26, 40-46)

3. **Update manifest:**
   - Edit `__manifest__.py`:
     - Change author name (line 12)
     - Update website URL (line 13)

4. **Install the module:**
   ```bash
   # Restart Odoo server
   # Then in Odoo UI: Apps > Update Apps List > Search "Custom Branding" > Install
   ```

## Customization Options

### Database Manager Page
- **Title:** Change in `controllers/database.py` line 22 (replace "Your Company Name")
- **Logo:** Replace `static/img/logo.png` with your logo

### Login Page
- **"Powered by" text:** Edit lines 20-26 in `templates.xml`
- Options:
  - Remove completely (uncomment `<t/>`)
  - Replace with custom text (uncomment and edit the `<a>` tag)

### POS Receipt
- **"Powered by Odoo" text:** Edit lines 40-46 in `templates.xml`
- Options:
  - Remove completely (uncomment `<t/>`)
  - Replace with custom text (uncomment and edit the `<p>` tag)

### Company Logo (Login & POS)
The company logo used in login page and POS is controlled by:
- **Settings > Companies > Your Company > Logo**
- Upload your logo there - no code changes needed

## Italian POS Module (Optional)

If you have `l10n_it_pos` module installed, you also need to override the JavaScript file:

1. Create: `static/src/js/fiscal_document_footer_override.js`
2. Add to `__manifest__.py` under assets:
   ```python
   'point_of_sale.assets': [
       'custom_branding/static/src/js/fiscal_document_footer_override.js',
   ],
   ```

See the example file `static/src/js/fiscal_document_footer_override.js.example` for reference.

## After Installation

1. **Clear browser cache**
2. **Restart Odoo server**
3. **Update assets** (if needed):
   ```bash
   odoo-bin -u custom_branding -d your_database
   ```

## Testing

After installation, check:
- [ ] Database selection page shows your logo and title
- [ ] Login page doesn't show "Powered by Odoo"
- [ ] POS receipts don't show "Powered by Odoo"
- [ ] Company logo is set via Settings > Companies

## Notes

- This module uses template inheritance, so it won't break during Odoo updates
- You can disable/uninstall the module to restore original branding
- All changes are in this module, no core files are modified

## Troubleshooting

**Logo not showing:**
- Check file path in `templates.xml`
- Ensure logo file exists in `static/img/logo.png`
- Clear browser cache
- Check Odoo logs for 404 errors

**Changes not appearing:**
- Restart Odoo server
- Update the module: `odoo-bin -u custom_branding -d your_database`
- Clear browser cache
- Check if module is installed and active

