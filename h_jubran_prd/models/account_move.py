from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Project Link (Many2one to your Project model)
    project_id = fields.Many2one(
        'h_jubran.project', 
        string='Project',
        tracking=True, 
        help='The main project linked to this invoice or bill.'
    )
    
    project_site = fields.Many2one(
        'stock.location',
        string='Project Site', 
        readonly=False,
        store=True,
        help="Site/Location of the linked project."
    )
    
    # Auto Complete PO field
    auto_complete_po_id = fields.Many2one(
        'purchase.order',
        string='Auto Complete PO',
        domain="[('state', 'in', ['purchase', 'done'])]",
        help="Select a Purchase Order to automatically populate invoice lines. Only shows confirmed Purchase Orders."
    )

    
    #Onchange Method for Site Auto-population
    # This logic executes when the project_id is changed
    @api.onchange('project_id')
    def _onchange_project_id_site(self):
        if self.project_id:
            # Set the site to the project's site field (which is a Many2one to stock.location)
            if hasattr(self.project_id, 'site') and self.project_id.site:
                self.project_site = self.project_id.site.id if hasattr(self.project_id.site, 'id') else self.project_id.site
        else:
            # Clear the site if no project is selected
            self.project_site = False
    
    @api.onchange('auto_complete_po_id')
    def _onchange_auto_complete_po_id(self):
        """Populate invoice lines from selected Purchase Order"""
        if not self.auto_complete_po_id or self.move_type != 'in_invoice':
            # Clear lines if PO is removed
            if not self.auto_complete_po_id:
                self.invoice_line_ids = [(5, 0, 0)]
            return
        
        po = self.auto_complete_po_id
        
        # Validate PO state
        if po.state not in ['purchase', 'done']:
            return {
                'warning': {
                    'title': _('Warning'),
                    'message': _('Selected Purchase Order must be in "Purchase" or "Done" state.')
                }
            }
        
        # Set partner if not already set
        if not self.partner_id:
            self.partner_id = po.partner_id
        
        # Set project from PO header if not already set
        if not self.project_id and hasattr(po, 'project_id') and po.project_id:
            self.project_id = po.project_id
        
        # Set project_site from PO's project_site (location) - this is the location from PO
        if hasattr(po, 'project_site') and po.project_site:
            self.project_site = po.project_site.id if hasattr(po.project_site, 'id') else po.project_site
        # Fallback: get from project if PO doesn't have project_site
        elif not self.project_site and self.project_id and hasattr(self.project_id, 'site') and self.project_id.site:
            self.project_site = self.project_id.site.id if hasattr(self.project_id.site, 'id') else self.project_id.site
        
        # Check if PO has lines
        if not po.order_line:
            return {
                'warning': {
                    'title': _('Warning'),
                    'message': _('Selected Purchase Order has no lines to invoice.')
                }
            }
        
        # Clear existing lines first to prevent duplication
        self.invoice_line_ids = [(5, 0, 0)]
        
        # Prepare invoice lines from PO lines
        invoice_lines = []
        for po_line in po.order_line:
            # Skip lines that have no quantity
            if po_line.product_qty <= 0:
                continue
            
            # Use full quantity from PO line (Odoo will handle already invoiced quantities)
            qty_to_invoice = po_line.product_qty
            
            # Skip if no quantity
            if qty_to_invoice <= 0:
                continue
            
            # Prepare invoice line values using Odoo's standard method
            line_vals = {}
            
            # Use purchase line's method to prepare invoice line (pass move for proper currency conversion)
            # IMPORTANT: We call the standard method first, then ADD our custom fields
            # CRITICAL: We need to prevent Odoo from auto-creating duplicate lines
            # The standard method sets purchase_line_id, which might trigger auto-creation on save
            if hasattr(po_line, '_prepare_account_move_line'):
                # Call with context to prevent auto-creation of duplicate lines
                line_vals = po_line.with_context(skip_purchase_auto_complete=True)._prepare_account_move_line(move=self)
                # Update quantity to our calculated quantity
                line_vals['quantity'] = qty_to_invoice
                # Remove account_id if it was set - we'll set it properly below
                # Actually, keep it - the standard method sets it correctly
            else:
                # Manual preparation if method doesn't exist
                # Get account from product or use default
                account_id = False
                if po_line.product_id:
                    account_id = po_line.product_id.property_account_expense_id.id or \
                               po_line.product_id.categ_id.property_account_expense_categ_id.id
                # If no account from product, get default expense account
                if not account_id:
                    account_id = self.env['account.account'].search([
                        ('user_type_id.type', '=', 'other'),
                        ('internal_type', '=', 'other'),
                        ('deprecated', '=', False)
                    ], limit=1).id
                
                line_vals = {
                    'product_id': po_line.product_id.id if po_line.product_id else False,
                    'name': po_line.name or (po_line.product_id.name if po_line.product_id else ''),
                    'quantity': qty_to_invoice,
                    'price_unit': po_line.price_unit or 0.0,
                    'product_uom_id': po_line.product_uom.id if po_line.product_uom else False,
                    'account_id': account_id,
                }
                
                # Link to purchase line if the field exists (standard Odoo field)
                # CRITICAL: We set this to link the line, but we need to prevent Odoo
                # from auto-creating duplicate lines when the invoice is saved.
                # The standard Odoo purchase module may auto-create lines when purchase_line_id is set.
                # We'll handle this in the write/create methods below.
                if 'purchase_line_id' in self.env['account.move.line']._fields:
                    line_vals['purchase_line_id'] = po_line.id
            
            # CRITICAL: ALWAYS copy ALL custom fields from PO line to invoice line
            # These fields are NOT included in the standard method, so we MUST add them
            # IMPORTANT: Set these fields AFTER calling standard method to ensure they're not overwritten
            
            # Master Data fields: Category, Subcategory, Element, Location
            # IMPORTANT: Access fields directly - they exist in our extended purchase.order.line model
            # We MUST set these AFTER the standard method to ensure they're not overwritten
            
            # Category - ALWAYS try to copy, even if empty
            try:
                if po_line.category_id:
                    line_vals['category_id'] = po_line.category_id.id
            except (AttributeError, KeyError):
                pass
            
            # Subcategory - ALWAYS try to copy, even if empty
            try:
                if po_line.subcategory_id:
                    line_vals['subcategory_id'] = po_line.subcategory_id.id
            except (AttributeError, KeyError):
                pass
            
            # Master Element
            if hasattr(po_line, 'master_element_id') and po_line.master_element_id:
                line_vals['master_element_id'] = po_line.master_element_id.id
            
            # Location
            if hasattr(po_line, 'location_id') and po_line.location_id:
                line_vals['location_id'] = po_line.location_id.id
            
            # Project-related fields from PO line
            # NOTE: project_id on account.move.line is a related field from move_id.project_id
            # So we don't set it here - it will be automatically set from the bill header
            # But we can still set it if needed for reference
            # if getattr(po_line, 'project_id', False):
            #     line_vals['project_id'] = po_line.project_id.id
            if getattr(po_line, 'stage_id', False):
                line_vals['po_stage_id'] = po_line.stage_id.id
                # Also set stage_id if it exists on account.move.line
                if 'stage_id' in self.env['account.move.line']._fields:
                    line_vals['stage_id'] = po_line.stage_id.id
            if getattr(po_line, 'substage_id', False):
                line_vals['po_substage_id'] = po_line.substage_id.id
            if getattr(po_line, 'element_id', False):
                line_vals['po_element_id'] = po_line.element_id.id
            
            # Ensure we have all required fields before appending
            # Make sure account_id is set (required field)
            if 'account_id' not in line_vals or not line_vals['account_id']:
                # Get default expense account
                if po_line.product_id:
                    line_vals['account_id'] = po_line.product_id.property_account_expense_id.id or \
                                           po_line.product_id.categ_id.property_account_expense_categ_id.id
            
            # Debug: Print line_vals to verify fields are being set
            # Uncomment for debugging:
            # import logging
            # _logger = logging.getLogger(__name__)
            # _logger.info(f"Line vals for PO line {po_line.id}: {line_vals}")
            
            invoice_lines.append((0, 0, line_vals))
        
        # Set invoice lines - replace all existing lines with new ones
        # IMPORTANT: Set in one operation to prevent duplication
        if invoice_lines:
            # Clear and set in a single assignment to avoid triggering multiple onchanges
            # Using (5, 0, 0) to clear all, then (0, 0, vals) to add new ones
            self.invoice_line_ids = [(5, 0, 0)] + invoice_lines
    
    def write(self, vals):
        """Override write to prevent duplicate invoice lines from purchase module"""
        # CRITICAL: When we save an invoice with purchase_line_id set on lines,
        # Odoo's purchase module may auto-create duplicate invoice lines.
        # We need to prevent this by checking if lines already have purchase_line_id.
        if 'invoice_line_ids' in vals and self.auto_complete_po_id:
            # Check if we already have invoice lines with purchase_line_id
            # If so, prevent Odoo from auto-creating duplicates
            existing_lines_with_po = self.invoice_line_ids.filtered(lambda l: l.purchase_line_id)
            if existing_lines_with_po:
                # Use context to prevent auto-creation
                self = self.with_context(skip_purchase_auto_complete=True, 
                                        from_auto_complete_po=True)
        result = super().write(vals)
        
        # After write, check for duplicates and remove them
        if self.auto_complete_po_id and self.invoice_line_ids:
            # Group lines by purchase_line_id and keep only the first one with category/subcategory
            lines_to_remove = []
            seen_po_lines = {}
            for line in self.invoice_line_ids:
                if line.purchase_line_id:
                    po_line_id = line.purchase_line_id.id
                    if po_line_id in seen_po_lines:
                        # This is a duplicate - check which one to keep
                        existing_line = seen_po_lines[po_line_id]
                        # Keep the one with category/subcategory, remove the one without
                        if line.category_id or line.subcategory_id:
                            # Current line has category, remove the existing one
                            if existing_line not in lines_to_remove:
                                lines_to_remove.append(existing_line)
                            seen_po_lines[po_line_id] = line
                        else:
                            # Current line doesn't have category, remove it
                            lines_to_remove.append(line)
                    else:
                        seen_po_lines[po_line_id] = line
            
            # Remove duplicate lines
            if lines_to_remove:
                # Convert list to recordset before unlinking
                self.env['account.move.line'].browse([line.id for line in lines_to_remove]).unlink()
        
        return result
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to prevent duplicate invoice lines from purchase module"""
        # When creating with auto_complete_po_id, prevent Odoo from auto-creating duplicates
        for vals in vals_list:
            if vals.get('auto_complete_po_id'):
                self = self.with_context(skip_purchase_auto_complete=True, 
                                        from_auto_complete_po=True)
        result = super().create(vals_list)
        
        # After create, check for duplicates and remove them
        for move in result:
            if move.auto_complete_po_id and move.invoice_line_ids:
                # Group lines by purchase_line_id and keep only the first one with category/subcategory
                lines_to_remove = []
                seen_po_lines = {}
                for line in move.invoice_line_ids:
                    if line.purchase_line_id:
                        po_line_id = line.purchase_line_id.id
                        if po_line_id in seen_po_lines:
                            # This is a duplicate - check which one to keep
                            existing_line = seen_po_lines[po_line_id]
                            # Keep the one with category/subcategory, remove the one without
                            if line.category_id or line.subcategory_id:
                                # Current line has category, remove the existing one
                                if existing_line not in lines_to_remove:
                                    lines_to_remove.append(existing_line)
                                seen_po_lines[po_line_id] = line
                            else:
                                # Current line doesn't have category, remove it
                                lines_to_remove.append(line)
                        else:
                            seen_po_lines[po_line_id] = line
                
                # Remove duplicate lines
                if lines_to_remove:
                    # Convert list to recordset before unlinking
                    self.env['account.move.line'].browse([line.id for line in lines_to_remove]).unlink()
        
        return result
    
    def action_post(self):
        """Override to update subcategory quantity and rate, and BOQ summary lines when vendor bill is confirmed"""
        _logger.info("=" * 80)
        _logger.info("VENDOR BILL CONFIRMATION DEBUG - Starting action_post")
        _logger.info("=" * 80)
        _logger.info(f"Vendor Bill ID: {self.id}")
        _logger.info(f"Vendor Bill Number: {self.name}")
        _logger.info(f"Move Type: {self.move_type}")
        _logger.info(f"State (before): {self.state}")
        _logger.info(f"Project ID: {self.project_id.id if self.project_id else 'None'}")
        _logger.info(f"Project Name: {self.project_id.name if self.project_id else 'None'}")
        _logger.info(f"Number of Invoice Lines: {len(self.invoice_line_ids)}")
        
        result = super().action_post()
        
        _logger.info(f"State (after super): {self.state}")
        
        # Only process vendor bills (in_invoice)
        if self.move_type == 'in_invoice':
            _logger.info("Processing vendor bill (in_invoice)")
            
            if not self.project_id:
                _logger.warning("No project_id set on vendor bill - skipping BOQ summary updates")
            
            # Group invoice lines by subcategory and project
            # invoice_line_ids filters by display_type in ('product', 'line_section', 'line_note')
            # After posting, invoice_line_ids still works correctly
            invoice_lines = self.invoice_line_ids.filtered(lambda l: l.display_type in ('product', False))
            
            subcategory_data = {}
            # Store lines by subcategory for later use
            lines_by_subcategory = {}
            
            _logger.info(f"Processing {len(invoice_lines)} invoice lines (from {len(self.invoice_line_ids)} invoice_line_ids, {len(self.line_ids)} line_ids)...")
            for idx, line in enumerate(invoice_lines):
                _logger.info(f"  Line {idx + 1}:")
                _logger.info(f"    - ID: {line.id}")
                _logger.info(f"    - Name: {line.name}")
                _logger.info(f"    - Product: {line.product_id.name if line.product_id else 'None'}")
                _logger.info(f"    - Subcategory ID: {line.subcategory_id.id if line.subcategory_id else 'None'}")
                _logger.info(f"    - Subcategory Name: {line.subcategory_id.name if line.subcategory_id else 'None'}")
                _logger.info(f"    - Quantity: {line.quantity}")
                _logger.info(f"    - Price Unit: {line.price_unit}")
                _logger.info(f"    - Price Subtotal: {line.price_subtotal}")
                _logger.info(f"    - Display Type: {line.display_type}")
                
                if line.subcategory_id:
                    subcategory_id = line.subcategory_id.id
                    project_id = self.project_id.id if self.project_id else False
                    key = (project_id, subcategory_id)
                    
                    if key not in subcategory_data:
                        subcategory_data[key] = {
                            'total_quantity': 0.0,
                            'total_amount': 0.0,
                            'lines': []  # Store lines for later use
                        }
                    # Sum quantity and amount for this subcategory
                    quantity = line.quantity or 0.0
                    amount = line.price_subtotal or (quantity * (line.price_unit or 0.0))
                    subcategory_data[key]['total_quantity'] += quantity
                    subcategory_data[key]['total_amount'] += amount
                    subcategory_data[key]['lines'].append(line)  # Store the line
                    _logger.info(f"    - Added to subcategory_data[{key}]: qty={quantity}, amount={amount}")
                else:
                    _logger.warning(f"    - SKIPPED: No subcategory_id on line")
            
            _logger.info(f"Found {len(subcategory_data)} unique project+subcategory combinations")
            
            # Update each subcategory with aggregated values from all confirmed vendor bills
            for (project_id, subcategory_id), data in subcategory_data.items():
                _logger.info("-" * 80)
                _logger.info(f"Processing Project ID: {project_id}, Subcategory ID: {subcategory_id}")
                _logger.info(f"Current bill data: qty={data['total_quantity']}, amount={data['total_amount']}")
                
                subcategory = self.env['h_jubran.master.subcategory'].browse(subcategory_id)
                _logger.info(f"Subcategory: {subcategory.name} (ID: {subcategory.id})")
                
                # CRITICAL FIX: Get current bill lines directly from invoice_line_ids (already collected)
                # Don't search for them - use the lines we already have from subcategory_data
                current_bill_lines = self.env['account.move.line']
                current_bill_line_ids = []
                if (project_id, subcategory_id) in subcategory_data:
                    # Use the lines we already collected - they're already in memory and have correct data
                    current_bill_lines = self.env['account.move.line'].browse([l.id for l in subcategory_data[(project_id, subcategory_id)]['lines']])
                    current_bill_line_ids = current_bill_lines.ids
                
                # Get OTHER bills' lines (exclude current bill) - these are already committed to DB
                # CRITICAL FIX: display_type='product' not False - need to match product lines
                other_bills_lines = self.env['account.move.line'].search([
                    ('subcategory_id', '=', subcategory_id),
                    ('move_id.move_type', '=', 'in_invoice'),
                    ('move_id.state', '=', 'posted'),
                    ('move_id', '!=', self.id),  # Exclude current bill
                ]).filtered(lambda l: l.display_type in ('product', False))  # Filter for product lines only
                
                # Combine: other bills + current bill
                # This ensures we aggregate ALL posted bills including the current one
                all_confirmed_lines = (other_bills_lines | current_bill_lines)
                
                _logger.info(f"=== AGGREGATION DEBUG for Subcategory {subcategory_id} ===")
                _logger.info(f"Current bill line IDs: {current_bill_line_ids}")
                _logger.info(f"Current bill lines found: {len(current_bill_lines)}")
                _logger.info(f"Other bills lines found: {len(other_bills_lines)}")
                _logger.info(f"Total confirmed lines (combined): {len(all_confirmed_lines)}")
                
                # Log current bill lines with details
                if current_bill_lines:
                    current_total_qty = sum(current_bill_lines.mapped('quantity'))
                    current_total_amt = sum(current_bill_lines.mapped('price_subtotal'))
                    _logger.info(f"Current bill totals: qty={current_total_qty}, amount={current_total_amt}")
                    for line in current_bill_lines:
                        _logger.info(f"  - Current: Line {line.id}, Bill {line.move_id.name}, qty={line.quantity}, amount={line.price_subtotal}")
                
                # Log other bills lines with details
                if other_bills_lines:
                    other_total_qty = sum(other_bills_lines.mapped('quantity'))
                    other_total_amt = sum(other_bills_lines.mapped('price_subtotal'))
                    _logger.info(f"Other bills totals: qty={other_total_qty}, amount={other_total_amt}")
                    for line in other_bills_lines[:5]:  # Log first 5
                        _logger.info(f"  - Other: Line {line.id}, Bill {line.move_id.name}, qty={line.quantity}, amount={line.price_subtotal}")
                
                # Log all lines combined
                _logger.info(f"All confirmed lines count: {len(all_confirmed_lines)}")
                for line in all_confirmed_lines[:10]:  # Log first 10
                    _logger.info(f"  - All: Line {line.id}, Bill {line.move_id.name}, qty={line.quantity}, amount={line.price_subtotal}")
                
                _logger.info(f"Total confirmed vendor bill lines for subcategory (all projects): {len(all_confirmed_lines)}")
                for line in all_confirmed_lines[:5]:  # Log first 5
                    _logger.info(f"  - Line {line.id}: qty={line.quantity}, amount={line.price_subtotal}, project={line.move_id.project_id.name if line.move_id.project_id else 'None'}")
                
                # Calculate total quantity and amount from all confirmed bills
                total_quantity = sum(all_confirmed_lines.mapped('quantity'))
                total_amount = sum(all_confirmed_lines.mapped('price_subtotal'))
                
                # Calculate weighted average rate
                weighted_rate = total_amount / total_quantity if total_quantity > 0 else 0.0
                
                _logger.info(f"Subcategory totals (all projects): qty={total_quantity}, amount={total_amount}, rate={weighted_rate}")
                _logger.info(f"Updating subcategory {subcategory_id} with: quantity={total_quantity}, rate={weighted_rate}")
                
                # Update subcategory
                subcategory.write({
                    'quantity': total_quantity,
                    'rate': weighted_rate
                })
                _logger.info(f"Subcategory updated successfully")
                
                # Update BOQ Summary Lines for this project + subcategory combination
                if project_id:
                    _logger.info(f"Searching for BOQ summary lines: project_id={project_id}, subcategory_id={subcategory_id}")
                    
                    # First, let's check all BOQ summary lines for this project
                    all_boq_lines_for_project = self.env['h_jubran.boq.summary.line'].search([
                        ('summary_id.project_id', '=', project_id)
                    ])
                    _logger.info(f"Total BOQ summary lines for project {project_id}: {len(all_boq_lines_for_project)}")
                    for boq_line in all_boq_lines_for_project[:5]:  # Log first 5
                        _logger.info(f"  - BOQ Line ID: {boq_line.id}, Code: {boq_line.code}, Subcategory ID: {boq_line.subcategory_id.id if boq_line.subcategory_id else 'None'}, Subcategory Name: {boq_line.subcategory_id.name if boq_line.subcategory_id else 'None'}")
                    
                    # Now search for lines with matching subcategory
                    boq_lines = self.env['h_jubran.boq.summary.line'].search([
                        ('summary_id.project_id', '=', project_id),
                        ('subcategory_id', '=', subcategory_id)
                    ])
                    
                    _logger.info(f"Found {len(boq_lines)} BOQ summary lines with matching subcategory")
                    for boq_line in boq_lines:
                        _logger.info(f"  - BOQ Line ID: {boq_line.id}, Code: {boq_line.code}, Summary: {boq_line.summary_id.name}")
                        _logger.info(f"    Current values: actual_qty={boq_line.actual_quantity}, actual_rate={boq_line.actual_rate}, actual_amount={boq_line.actual_amount}")
                    
                    if boq_lines:
                        # CRITICAL FIX: Get current bill lines directly from invoice_line_ids (already collected)
                        # Don't search for them - use the lines we already have from subcategory_data
                        current_bill_lines = self.env['account.move.line']
                        current_bill_line_ids = []
                        if (project_id, subcategory_id) in subcategory_data:
                            # Use the lines we already collected - they're already in memory and have correct data
                            current_bill_lines = self.env['account.move.line'].browse([l.id for l in subcategory_data[(project_id, subcategory_id)]['lines']])
                            current_bill_line_ids = current_bill_lines.ids
                        
                        # Get OTHER bills' lines for this project (exclude current bill) - these are already committed to DB
                        # CRITICAL FIX: display_type='product' not False - need to match product lines
                        other_project_bills_lines = self.env['account.move.line'].search([
                            ('subcategory_id', '=', subcategory_id),
                            ('move_id.move_type', '=', 'in_invoice'),
                            ('move_id.state', '=', 'posted'),
                            ('move_id.project_id', '=', project_id),
                            ('move_id', '!=', self.id),  # Exclude current bill
                        ]).filtered(lambda l: l.display_type in ('product', False))  # Filter for product lines only
                        
                        # Combine: other bills + current bill
                        # This ensures we aggregate ALL posted bills including the current one
                        project_confirmed_lines = (other_project_bills_lines | current_bill_lines)
                        
                        _logger.info(f"=== BOQ AGGREGATION DEBUG for Project {project_id}, Subcategory {subcategory_id} ===")
                        _logger.info(f"Current bill line IDs: {current_bill_line_ids}")
                        _logger.info(f"Current bill lines found: {len(current_bill_lines)}")
                        _logger.info(f"Other bills lines found: {len(other_project_bills_lines)}")
                        _logger.info(f"Total project confirmed lines (combined): {len(project_confirmed_lines)}")
                        
                        # Log current bill lines with details
                        if current_bill_lines:
                            current_total_qty = sum(current_bill_lines.mapped('quantity'))
                            current_total_amt = sum(current_bill_lines.mapped('price_subtotal'))
                            _logger.info(f"Current bill totals: qty={current_total_qty}, amount={current_total_amt}")
                            for line in current_bill_lines:
                                _logger.info(f"  - Current: Line {line.id}, Bill {line.move_id.name}, qty={line.quantity}, amount={line.price_subtotal}")
                        
                        # Log other bills lines with details
                        if other_project_bills_lines:
                            other_total_qty = sum(other_project_bills_lines.mapped('quantity'))
                            other_total_amt = sum(other_project_bills_lines.mapped('price_subtotal'))
                            _logger.info(f"Other bills totals: qty={other_total_qty}, amount={other_total_amt}")
                            for line in other_project_bills_lines[:5]:  # Log first 5
                                _logger.info(f"  - Other: Line {line.id}, Bill {line.move_id.name}, qty={line.quantity}, amount={line.price_subtotal}")
                        
                        # Log all lines combined
                        _logger.info(f"All project confirmed lines count: {len(project_confirmed_lines)}")
                        for line in project_confirmed_lines[:10]:  # Log first 10
                            _logger.info(f"  - All: Line {line.id}, Bill {line.move_id.name}, qty={line.quantity}, amount={line.price_subtotal}")
                        
                        _logger.info(f"Found {len(project_confirmed_lines)} confirmed vendor bill lines for project {project_id} + subcategory {subcategory_id}")
                        for line in project_confirmed_lines[:5]:  # Log first 5
                            _logger.info(f"  - Line {line.id}: qty={line.quantity}, amount={line.price_subtotal}, bill={line.move_id.name}")
                        
                        # Calculate aggregated values for this project + subcategory
                        project_total_quantity = sum(project_confirmed_lines.mapped('quantity'))
                        project_total_amount = sum(project_confirmed_lines.mapped('price_subtotal'))
                        project_weighted_rate = project_total_amount / project_total_quantity if project_total_quantity > 0 else 0.0
                        
                        _logger.info(f"Project totals: qty={project_total_quantity}, amount={project_total_amount}, rate={project_weighted_rate}")
                        _logger.info(f"Updating {len(boq_lines)} BOQ summary lines with: actual_quantity={project_total_quantity}, actual_rate={project_weighted_rate}, actual_amount={project_total_amount}")
                        
                        # Update all matching BOQ summary lines
                        boq_lines.write({
                            'actual_quantity': project_total_quantity,
                            'actual_rate': project_weighted_rate,
                            'actual_amount': project_total_amount
                        })
                        _logger.info(f"BOQ summary lines updated successfully")
                        
                        # Verify the update
                        for boq_line in boq_lines:
                            boq_line.invalidate_recordset(['actual_quantity', 'actual_rate', 'actual_amount'])
                            _logger.info(f"  - BOQ Line {boq_line.id} after update: actual_qty={boq_line.actual_quantity}, actual_rate={boq_line.actual_rate}, actual_amount={boq_line.actual_amount}")
                    else:
                        _logger.warning(f"No BOQ summary lines found for project_id={project_id}, subcategory_id={subcategory_id}")
                else:
                    _logger.warning("No project_id - skipping BOQ summary line updates")
        
        _logger.info("=" * 80)
        _logger.info("VENDOR BILL CONFIRMATION DEBUG - Completed action_post")
        _logger.info("=" * 80)
        
        return result
            
    
    # Stage Link (Many2one to your Global Stage model)
    # This field is generally not strictly needed on the header, but useful for filtering.
    # We will primarily focus on the line items for stages.
    # stage_id = fields.Many2one(
    #     'h_jubran.project.stage.global', 
    #     string='Project Stage', 
    #     tracking=True
    # )

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Project Link: Inherits from the header and is available for reporting
    project_id = fields.Many2one(
        'h_jubran.project', 
        string='Project',
        store=True, 
        readonly=True, 
        related='move_id.project_id' # Automatically populated from the Invoice header
    )

    # Stage Link: This is the crucial field for detailed tracking on the line item level
    stage_id = fields.Many2one(
        'h_jubran.project.stage.global', 
        string='Project Stage',
        domain="[('id', 'in', allowed_stage_ids)]", # Apply dynamic domain
        help='The specific project stage related to this line item cost/revenue.'
    )
    
    # Technical field for dynamic domain filtering on stages
    allowed_stage_ids = fields.Many2many(
        'h_jubran.project.stage.global', 
        compute='_compute_allowed_stage_ids'
    )

    def _compute_allowed_stage_ids(self):
        """
        Calculates the stages available for selection on the line item.
        If a project is selected on the Invoice/Bill, only the stages present 
        in that project's structure should be selectable.
        """
        for line in self:
            if line.project_id:
                # Get the stage IDs from the project's stage_line_ids
                project_stage_lines = self.env['h_jubran.project.stage.line'].search([
                    ('project_id', '=', line.project_id.id)
                ])
                stage_ids = project_stage_lines.stage_id.ids
                line.allowed_stage_ids = [(6, 0, stage_ids)]
            else:
                # If no project is selected, allow all active stages (or restrict to empty)
                line.allowed_stage_ids = self.env['h_jubran.project.stage.global'].search([('is_active', '=', True)]).ids

    boq_summary_line_id = fields.Many2one(
        'h_jubran.boq.summary.line',
        string='BOQ Summary Line',
        ondelete='set null'
    )
    boq_number = fields.Char(string='BOQ Number')
    boq_code = fields.Char(string='BOQ Code')
    boq_scope = fields.Char(string='BOQ Scope')
    boq_category_id = fields.Many2one(
        'h_jubran.master.category',
        string='BOQ Category',
        ondelete='restrict'
    )
    boq_amount = fields.Monetary(
        string='BOQ Amount',
        currency_field='company_currency_id'
    )
    boq_actual_amount = fields.Monetary(
        string='BOQ Actual Amount',
        currency_field='company_currency_id'
    )
    
    # Fields from Purchase Order Lines
    category_id = fields.Many2one(
        'h_jubran.master.category',
        string='Category',
        help="Master data category from purchase order."
    )
    
    subcategory_id = fields.Many2one(
        'h_jubran.master.subcategory',
        string='Sub-Category',
        domain="[('category_id', '=', category_id)]",
        help="Master data subcategory from purchase order."
    )
    
    master_element_id = fields.Many2one(
        'h_jubran.master.element',
        string='Element',
        domain="[('subcategory_id', '=', subcategory_id)]",
        help="Master data element from purchase order."
    )
    
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
        domain="[('usage', 'in', ['internal', 'transit'])]",
        help="Location from purchase order line."
    )
    
    # Project-related fields from PO
    po_stage_id = fields.Many2one(
        'h_jubran.project.stage.global',
        string='PO Stage',
        help="Stage from purchase order line."
    )
    
    po_substage_id = fields.Many2one(
        'h_jubran.project.stage.global',
        string='PO Substage',
        help="Substage from purchase order line."
    )
    
    po_element_id = fields.Many2one(
        'h_jubran.project.element.global',
        string='PO Element',
        help="Element from purchase order line."
    )