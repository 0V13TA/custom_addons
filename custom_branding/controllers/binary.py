# -*- coding: utf-8 -*-

import base64
import logging
import psycopg2
from odoo import http
from odoo.addons.web.controllers import binary as binary_controller
from odoo.http import request
from odoo.tools.misc import file_open
from odoo.tools import config

_logger = logging.getLogger(__name__)


class Binary(binary_controller.Binary):
    """Override binary controller to serve database logo"""

    @http.route(['/custom_branding/database_logo'], type='http', auth="none", csrf=False)
    def database_logo(self, db=None, **kwargs):
        """Serve the database page logo"""
        if not db:
            _logger.warning("[Custom Branding] No database specified for logo request")
            return self._serve_default_logo()
        
        # Try using registry first (faster if available)
        try:
            import odoo
            registry = odoo.registry(db)
            with registry.cursor() as cr:
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                company = env['res.company'].sudo().search([
                    ('database_page_logo', '!=', False)
                ], limit=1, order='id')
                if company and company.database_page_logo:
                    image_base64 = company.database_page_logo
                    image_data = base64.b64decode(image_base64)
                    _logger.info("[Custom Branding] Serving logo from registry for DB: %s", db)
                    return request.make_response(
                        image_data,
                        headers=[
                            ('Content-Type', 'image/png'),
                            ('Content-Length', str(len(image_data))),
                            ('Cache-Control', 'public, max-age=3600'),
                        ]
                    )
        except Exception as e:
            _logger.debug("[Custom Branding] Registry method failed for %s: %s", db, str(e))
        
        # Fallback to direct SQL connection
        try:
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
                            dbname=db,
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
                conn = psycopg2.connect(
                    dbname=db,
                    user=db_user,
                    password=db_password,
                    host=db_host,
                    port=db_port,
                    connect_timeout=3
                )
            
            if conn:
                cr = conn.cursor()
                # Check if column exists
                cr.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='res_company' 
                    AND column_name='database_page_logo'
                """)
                
                if cr.fetchone():
                    cr.execute("""
                        SELECT database_page_logo
                        FROM res_company
                        WHERE database_page_logo IS NOT NULL
                        ORDER BY id
                        LIMIT 1
                    """)
                    row = cr.fetchone()
                    if row and row[0]:
                        image_data = base64.b64decode(row[0])
                        cr.close()
                        conn.close()
                        _logger.info("[Custom Branding] Serving logo from SQL for DB: %s", db)
                        return request.make_response(
                            image_data,
                            headers=[
                                ('Content-Type', 'image/png'),
                                ('Content-Length', str(len(image_data))),
                                ('Cache-Control', 'public, max-age=3600'),
                            ]
                        )
                cr.close()
                conn.close()
        except Exception as e:
            _logger.warning("[Custom Branding] SQL method failed for %s: %s", db, str(e))
        
        # Fallback to default logo
        return self._serve_default_logo()
    
    def _serve_default_logo(self):
        """Serve the default Odoo logo"""
        try:
            with file_open('web/static/img/logo2.png', 'rb') as f:
                logo_data = f.read()
                return request.make_response(
                    logo_data,
                    headers=[
                        ('Content-Type', 'image/png'),
                        ('Content-Length', str(len(logo_data))),
                        ('Cache-Control', 'public, max-age=3600'),
                    ]
                )
        except Exception as e:
            _logger.error("[Custom Branding] Could not serve default logo: %s", str(e))
            return request.not_found()

