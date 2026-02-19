# -*- coding: utf-8 -*-

import re
import psycopg2
import logging
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers import database as database_controller
from odoo.tools import config

_logger = logging.getLogger(__name__)


class Database(database_controller.Database):
    """Override database controller to use custom branding"""

    def _get_branding_from_db(self, db_name):
        """Get branding settings from a specific database using direct SQL"""
        database_page_title = None
        database_page_logo = None
        
        try:
            # Get DB connection params from Odoo config
            db_user = config.get('db_user', 'odoo')
            db_password = config.get('db_password', 'odoo')
            db_host = config.get('db_host', 'localhost')
            db_port = int(config.get('db_port', 5432))
            
            # Handle Docker and various host configurations
            conn = None
            if db_host in ('False', '', None):
                # Try common Docker service names
                for docker_host in ['db-odoo18', 'db', 'postgres', 'localhost']:
                    try:
                        conn = psycopg2.connect(
                            dbname=db_name,
                            user=db_user,
                            password=db_password,
                            host=docker_host,
                            port=db_port,
                            connect_timeout=3
                        )
                        break
                    except psycopg2.Error:
                        continue
            else:
                # Use configured host
                conn = psycopg2.connect(
                    dbname=db_name,
                    user=db_user,
                    password=db_password,
                    host=db_host,
                    port=db_port,
                    connect_timeout=3
                )
            
            if not conn:
                _logger.warning("[Custom Branding] Could not connect to database %s", db_name)
                return None, None
                
            cr = conn.cursor()
            
            # Check if the table and columns exist
            cr.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='res_company' 
                AND column_name IN ('database_page_title', 'database_page_logo')
            """)
            
            columns = [row[0] for row in cr.fetchall()]
            has_title_col = 'database_page_title' in columns
            has_logo_col = 'database_page_logo' in columns
            
            if has_title_col or has_logo_col:
                # Build query based on available columns
                select_fields = []
                if has_title_col:
                    select_fields.append('database_page_title')
                if has_logo_col:
                    select_fields.append('database_page_logo')
                
                cr.execute(f"""
                    SELECT {', '.join(select_fields)}
                    FROM res_company
                    WHERE (database_page_title IS NOT NULL AND database_page_title != '') 
                       OR (database_page_logo IS NOT NULL)
                    ORDER BY id
                    LIMIT 1
                """)
                row = cr.fetchone()
                if row:
                    if has_title_col:
                        idx = select_fields.index('database_page_title')
                        if row[idx]:
                            database_page_title = row[idx].strip() if row[idx] else None
                    if has_logo_col:
                        idx = select_fields.index('database_page_logo')
                        if row[idx]:
                            database_page_logo = row[idx]
            
            cr.close()
            conn.close()
            
            _logger.info("[Custom Branding] Retrieved from DB %s - Title: %s, Logo: %s", 
                        db_name, 
                        database_page_title if database_page_title else "None",
                        "Present" if database_page_logo else "None")
            
        except psycopg2.Error as e:
            _logger.warning("[Custom Branding] Database connection error for %s: %s", db_name, str(e))
        except Exception as e:
            _logger.warning("[Custom Branding] Error getting branding from database %s: %s", db_name, str(e))
        
        return database_page_title, database_page_logo

    def _render_template(self, **d):
        """Override to use custom database manager template"""
        # Call parent method to get all the data and render template
        try:
            result = super()._render_template(**d)
        except Exception as e:
            _logger.error("[Custom Branding] Error in parent _render_template: %s", str(e))
            raise
        
        # If result is not a string (e.g., it's a Response object), return it as-is
        if not isinstance(result, str):
            return result
        
        # Get company settings from available databases using direct SQL
        database_page_title = None
        database_page_logo = None
        db_name = None
        
        try:
            databases = http.db_list()
            if databases:
                # Try each database until we find one with branding settings
                for db in databases:
                    title, logo = self._get_branding_from_db(db)
                    if title or logo:
                        database_page_title = title
                        database_page_logo = logo
                        db_name = db
                        break
                    # If no branding found, use first database for logo URL
                    if not db_name:
                        db_name = db
        except Exception as e:
            _logger.warning("[Custom Branding] Error getting database list: %s", str(e))
        
        # Replace title using regex for more robust matching
        if database_page_title and database_page_title.strip():
            try:
                # Match <title>Odoo</title> with any whitespace variations
                result = re.sub(
                    r'<title>\s*Odoo\s*</title>',
                    f'<title>{database_page_title}</title>',
                    result,
                    flags=re.IGNORECASE
                )
                _logger.info("[Custom Branding] Replaced title with: %s", database_page_title)
            except Exception as e:
                _logger.warning("[Custom Branding] Error replacing title: %s", str(e))
        
        # Replace logo with logo + title side by side
        if db_name:
            try:
                #logo_url = f'/custom_branding/database_logo?db={db_name}'
                logo_url = '/custom_branding/static/img/logo.png'
                # Get title for display (use custom title if available, otherwise use database name)
                display_title = database_page_title if database_page_title and database_page_title.strip() else db_name
                
                # Replace the img tag with a flex container containing logo and title
                logo_title_html = f'''<div class="d-flex align-items-center justify-content-center gap-3 mb-3" style="flex-wrap: wrap;">
                    <img src="{logo_url}" class="img-fluid" style="max-width: 200px; max-height: 80px; width: auto; height: auto;"/>
                    <h2 class="mb-0" style="font-size: 2rem; font-weight: 600; color: #333;">{display_title}</h2>
                </div>'''
                
                result = re.sub(
                    r'<img\s+src=["\']/web/static/img/logo2\.png["\'][^>]*>',
                    logo_title_html,
                    result,
                    flags=re.IGNORECASE
                )
                
                if database_page_logo:
                    _logger.info("[Custom Branding] Replaced logo with custom logo and title from DB: %s", db_name)
                else:
                    _logger.debug("[Custom Branding] Replaced logo URL with title (using default logo)")
            except Exception as e:
                _logger.warning("[Custom Branding] Error replacing logo with title: %s", str(e))
        
        return result
    
    @http.route('/web/database/selector', type='http', auth="none")
    def selector(self, **kw):
        """Override selector route to use custom branding"""
        if request.db:
            request.env.cr.close()
        return self._render_template(manage=False)
    
    @http.route('/web/database/manager', type='http', auth="none")
    def manager(self, **kw):
        """Override manager route to use custom branding"""
        if request.db:
            request.env.cr.close()
        return self._render_template()

