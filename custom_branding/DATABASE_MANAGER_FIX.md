# Database Manager Page Customization Fix

## Problem
The database manager page (both `/web/database/selector` and `/web/database/manager`) was not showing custom logo and title despite settings being configured.

## Root Causes Identified

1. **String Replacement Too Simple**: The original code used simple `str.replace()` which failed if there were whitespace variations or different quote styles in the HTML
2. **Database Connection Issues**: The connection logic had bugs and didn't handle Docker environments properly
3. **Logo Serving Unreliable**: The binary controller only tried one method and failed silently
4. **Limited Error Logging**: Errors were logged at debug level, making troubleshooting difficult

## Fixes Applied

### 1. Enhanced `controllers/database.py`

**Improvements:**
- ✅ **Regex-based replacement**: Uses `re.sub()` with patterns that handle whitespace variations
- ✅ **Better database connection**: Tries multiple Docker hostnames automatically (`db-odoo18`, `db`, `postgres`, `localhost`)
- ✅ **Multiple database support**: Tries all databases until it finds one with branding settings
- ✅ **Improved logging**: Changed from `debug` to `info`/`warning` levels for better visibility
- ✅ **Robust title replacement**: Pattern `r'<title>\s*Odoo\s*</title>'` handles any whitespace
- ✅ **Robust logo replacement**: Pattern `r'src=["\']/web/static/img/logo2\.png["\']'` handles single/double quotes

**Key Changes:**
```python
# Before: Simple string replace
result = result.replace('<title>Odoo</title>', f'<title>{title}</title>')

# After: Regex with whitespace handling
result = re.sub(
    r'<title>\s*Odoo\s*</title>',
    f'<title>{database_page_title}</title>',
    result,
    flags=re.IGNORECASE
)
```

### 2. Enhanced `controllers/binary.py`

**Improvements:**
- ✅ **Dual method approach**: Tries registry method first (faster), falls back to direct SQL
- ✅ **Better Docker support**: Same multi-hostname logic as database.py
- ✅ **Proper error handling**: Each method has try/except with appropriate logging
- ✅ **Cache headers**: Added `Cache-Control` headers for better performance
- ✅ **Content-Length headers**: Properly formatted for HTTP compliance

**Key Changes:**
```python
# Before: Only registry method, silent failure
try:
    registry = odoo.registry(db)
    # ... get logo
except Exception:
    pass  # Silent failure

# After: Registry + SQL fallback with logging
try:
    registry = odoo.registry(db)
    # ... get logo
except Exception as e:
    _logger.debug("Registry failed: %s", str(e))
    # Fallback to SQL method...
```

## Testing Instructions

### Step 1: Configure Branding Settings

1. Go to **Settings** (⚙️ icon)
2. Scroll to **Custom Branding** section
3. Configure:
   - **Database Page Logo**: Upload your logo image
   - **Database Page Title**: Enter your company name (e.g., "My Company")
4. Click **Save**

### Step 2: Verify Database Columns

Check that the columns exist in your database:
```sql
SELECT column_name 
FROM information_schema.columns 
WHERE table_name='res_company' 
AND column_name IN ('database_page_title', 'database_page_logo');
```

Should return 2 rows.

### Step 3: Check Settings Are Saved

```sql
SELECT database_page_title, 
       CASE WHEN database_page_logo IS NOT NULL THEN 'Logo Present' ELSE 'No Logo' END as logo_status
FROM res_company
LIMIT 1;
```

Should show your title and "Logo Present".

### Step 4: Test Database Selector Page

1. **Clear browser cache** (Ctrl+Shift+R or Cmd+Shift+R)
2. Visit: `http://your-server:port/web/database/selector`
3. **Expected Results:**
   - Browser tab title shows your custom title (not "Odoo")
   - Logo image shows your custom logo (not Odoo logo)

### Step 5: Test Database Manager Page

1. Visit: `http://your-server:port/web/database/manager`
2. **Expected Results:**
   - Browser tab title shows your custom title
   - Logo image shows your custom logo

### Step 6: Check Logs

Check Odoo logs for confirmation messages:
```bash
grep "Custom Branding" /path/to/odoo.log
```

You should see messages like:
```
[Custom Branding] Retrieved from DB your_db - Title: Your Company, Logo: Present
[Custom Branding] Replaced title with: Your Company
[Custom Branding] Replaced logo with custom logo from DB: your_db
```

## Troubleshooting

### Logo Not Showing

1. **Check logo URL is accessible:**
   ```
   http://your-server:port/custom_branding/database_logo?db=your_database_name
   ```
   Should return image data (not 404)

2. **Check browser console:**
   - Open Developer Tools (F12)
   - Check Network tab for logo request
   - Verify it returns 200 status

3. **Check Odoo logs:**
   ```bash
   grep -i "custom branding" /path/to/odoo.log | tail -20
   ```

4. **Verify database connection:**
   - Check `db_host`, `db_user`, `db_password` in Odoo config
   - For Docker: Ensure service name matches (`db-odoo18`, `db`, etc.)

### Title Not Showing

1. **Check HTML source:**
   - View page source (Ctrl+U)
   - Search for `<title>`
   - Should show your custom title

2. **Verify title is saved:**
   ```sql
   SELECT database_page_title FROM res_company LIMIT 1;
   ```

3. **Check logs for replacement:**
   ```bash
   grep "Replaced title" /path/to/odoo.log
   ```

### Both Not Working

1. **Restart Odoo server:**
   ```bash
   # Restart your Odoo service
   sudo systemctl restart odoo
   # Or if using Docker:
   docker-compose restart odoo
   ```

2. **Update the module:**
   ```bash
   odoo-bin -u custom_branding -d your_database
   ```

3. **Clear browser cache completely:**
   - Use incognito/private window
   - Or clear all cached images and files

4. **Check module is installed:**
   - Go to Apps menu
   - Search "Custom Branding"
   - Verify it's installed and active

## Technical Details

### How It Works

1. **Database Page Request** (`/web/database/selector` or `/web/database/manager`):
   - Odoo calls `Database._render_template()`
   - Our override intercepts this call
   - Gets branding from database using direct SQL
   - Replaces title and logo URL in HTML using regex
   - Returns modified HTML

2. **Logo Image Request** (`/custom_branding/database_logo?db=...`):
   - Browser requests logo image
   - Our binary controller serves it
   - Tries registry method first (faster)
   - Falls back to direct SQL if registry unavailable
   - Returns image data with proper headers

### Why Direct SQL?

The database manager page loads **before** Odoo registry is initialized, so we can't use normal Odoo ORM. Direct SQL connection allows us to:
- Access database before registry is ready
- Work in Docker environments
- Handle multiple databases gracefully

### Regex Patterns Explained

**Title Pattern:**
```python
r'<title>\s*Odoo\s*</title>'
```
- `\s*` matches any whitespace (spaces, tabs, newlines)
- Handles: `<title>Odoo</title>`, `<title> Odoo </title>`, etc.

**Logo Pattern:**
```python
r'src=["\']/web/static/img/logo2\.png["\']'
```
- `["\']` matches either single or double quote
- `\.` escapes the dot (literal period)
- Handles: `src="/web/static/img/logo2.png"`, `src='/web/static/img/logo2.png'`

## Files Modified

1. ✅ `custom_branding/controllers/database.py` - Enhanced template rendering
2. ✅ `custom_branding/controllers/binary.py` - Enhanced logo serving

## Next Steps

After applying these fixes:

1. ✅ Restart Odoo server
2. ✅ Update module: `odoo-bin -u custom_branding -d your_database`
3. ✅ Clear browser cache
4. ✅ Test both `/web/database/selector` and `/web/database/manager`
5. ✅ Check logs for confirmation messages

## Support

If issues persist:
1. Check Odoo logs for error messages
2. Verify database connection settings
3. Ensure module is properly installed
4. Test logo URL directly in browser
5. Check browser console for JavaScript errors

