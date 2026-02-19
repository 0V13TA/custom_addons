from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # 1. Link to your custom project model (h_jubran.project)
    project_id = fields.Many2one(
        'h_jubran.project', 
        string='Project', 
        required=False, # Set to True if every PO must be linked to a project
        tracking=True,
        help="Link the Purchase Order to a specific custom project for cost tracking."
    )
    
    # 2. Project Site field (will be auto-populated)
    # NOTE: We use a simple field and an @api.onchange method for the site,
    # as requested in your note, instead of a 'related' field.    
    project_site = fields.Many2one(
        'stock.location',
        string='Project Site (Location)',
        readonly=False,
        store=True,
        help="Site/Location of the linked project."
    )
    
    # 3. Purchase Request Number (computed from order lines)
    purchase_request_ids = fields.Many2many(
        'h_jubran.purchase.request',
        compute='_compute_purchase_request_ids',
        string='Purchase Request(s)',
        readonly=True,
        store=False,
        help="Purchase Requests linked to this Purchase Order"
    )
    
    purchase_request_names = fields.Char(
        string='Purchase Request Number(s)',
        compute='_compute_purchase_request_names',
        store=False,
        readonly=True,
        help="Purchase Request reference numbers"
    )
    
    # Auto Complete PR field
    auto_complete_pr_id = fields.Many2one(
        'h_jubran.purchase.request',
        string='Auto Complete PR',
        domain="[('state', '=', 'done'), ('used_in_confirmed_po', '=', False)]",
        help="Select a Purchase Request to automatically populate purchase order lines. Only shows Purchase Requests in 'Done' state that haven't been used in confirmed Purchase Orders."
    )
    
    @api.model
    def _get_available_purchase_requests(self):
        """Get domain for available Purchase Requests (not used in confirmed POs) - for onchange"""
        return [('state', '=', 'done'), ('used_in_confirmed_po', '=', False)]
    
    
    @api.depends('order_line.purchase_lines.request_id')
    def _compute_purchase_request_ids(self):
        for order in self:
            request_ids = order.order_line.mapped('purchase_lines.request_id').ids
            order.purchase_request_ids = [(6, 0, request_ids)]

    @api.depends('order_line.purchase_lines.request_id')
    def _compute_purchase_request_names(self):
        for order in self:
            requests = order.order_line.mapped('purchase_lines.request_id')
            if requests:
                order.purchase_request_names = ', '.join(requests.mapped('name'))
            else:
                order.purchase_request_names = False
    
    @api.onchange('auto_complete_pr_id')
    def _onchange_auto_complete_pr_id(self):
        """Populate purchase order lines from selected Purchase Request"""
        if not self.auto_complete_pr_id:
            # Clear lines if PR is removed
            self.order_line = [(5, 0, 0)]
            return
        
        pr = self.auto_complete_pr_id
        
        # Only allow in draft/sent states
        if self.state not in ['draft', 'sent']:
            return
        
        # Set partner if not already set (get from first line's product vendor or use default)
        if not self.partner_id:
            # Try to get vendor from PR lines
            for line in pr.line_ids:
                if line.product_id and line.product_id.seller_ids:
                    self.partner_id = line.product_id.seller_ids[0].partner_id
                    break
            # If still no partner, use first vendor
            if not self.partner_id:
                partner = self.env['res.partner'].search([('supplier_rank', '>', 0)], limit=1)
                if partner:
                    self.partner_id = partner
        
        # Set project from PR header if not already set
        if not self.project_id and pr.project_id:
            self.project_id = pr.project_id
            self._onchange_project_id_site()
        
        # Set project_site from PR header
        if pr.project_site:
            self.project_site = pr.project_site.id if hasattr(pr.project_site, 'id') else pr.project_site
        
        # Check if PR has lines
        if not pr.line_ids:
            return {
                'warning': {
                    'title': _('Warning'),
                    'message': _('Selected Purchase Request has no lines.')
                }
            }
        
        # Clear existing lines first to prevent duplication
        self.order_line = [(5, 0, 0)]
        
        # Prepare PO lines from PR lines
        po_lines = []
        for pr_line in pr.line_ids:
            # Skip cancelled lines or lines with no pending quantity
            if pr_line.cancelled or pr_line.pending_qty_to_receive <= 0:
                continue
            
            # Prepare PO line values
            line_vals = {
                'product_id': pr_line.product_id.id if pr_line.product_id else False,
                'name': pr_line.name or (pr_line.product_id.name if pr_line.product_id else ''),
                'product_qty': pr_line.pending_qty_to_receive,
                'product_uom': pr_line.product_uom_id.id if pr_line.product_uom_id else False,
                'price_unit': pr_line.rate if pr_line.rate else 0.0,
                'date_planned': pr_line.date_required or fields.Datetime.now(),
            }
            
            # CRITICAL: Copy ALL custom fields from PR line to PO line
            if pr_line.category_id:
                line_vals['category_id'] = pr_line.category_id.id
            if pr_line.subcategory_id:
                line_vals['subcategory_id'] = pr_line.subcategory_id.id
            if pr_line.master_element_id:
                line_vals['master_element_id'] = pr_line.master_element_id.id
            if pr_line.boq_rate:
                line_vals['boq_rate'] = pr_line.boq_rate
            
            po_lines.append((0, 0, line_vals))
        
        # Set PO lines - replace all existing lines with new ones
        if po_lines:
            self.order_line = po_lines
            
            # Link PR lines to PO lines after creation
            for po_line, pr_line in zip(self.order_line, pr.line_ids.filtered(lambda l: not l.cancelled and l.pending_qty_to_receive > 0)):
                if pr_line:
                    po_line.purchase_lines = [(4, pr_line.id)]

    
    #Onchange Method for Site Auto-population
    # This logic executes when the project_id is changed
    @api.onchange('project_id')
    def _onchange_project_id_site(self):
        if self.project_id:
            # Set the site to the project's site field
            self.project_site = self.project_id.site
            
            # Optionally, you can also auto-set the analytic account if not using compute/related
            # self.analytic_account_id = self.project_id.analytic_account_id 
            
        else:
            # Clear the site if no project is selected
            self.project_site = False
    
    def write(self, vals):
        """Override write to recompute used_in_confirmed_po when PO state changes"""
        result = super().write(vals)
        # If state is changing to 'purchase' or 'done', recompute PRs
        if 'state' in vals and vals['state'] in ['purchase', 'done']:
            # Recompute all PRs in 'done' state to ensure the field is up to date
            all_prs = self.env['h_jubran.purchase.request'].search([('state', '=', 'done')])
            if all_prs:
                all_prs.sudo()._compute_used_in_confirmed_po()
        return result
    
    def button_confirm(self):
        """Override to update BOQ actual costs when PO is confirmed and mark PR as used"""
        result = super().button_confirm()
        # Update BOQ lines for all PO lines with subcategory
        for line in self.order_line:
            if line.subcategory_id and line.project_id:
                line._update_boq_actual_costs()
        
        # Recompute used_in_confirmed_po for all PRs that might be affected
        # This ensures the field is updated when PO state changes to 'purchase' or 'done'
        # Recompute all PRs in 'done' state to ensure the field is up to date
        all_prs = self.env['h_jubran.purchase.request'].search([('state', '=', 'done')])
        if all_prs:
            all_prs.sudo()._compute_used_in_confirmed_po()
        
        return result

# --- Purchase Order Line Extension ---

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # Override product_id to make it optional when subcategory is provided
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=False,  # Make optional
        domain="[('purchase_ok', '=', True)]",
        change_default=True,
        index='btree_not_null',
    )
    
    # 1. Related Project ID (from the header)
    project_id = fields.Many2one(
        'h_jubran.project',
        string='Project',
        related='order_id.project_id',
        store=True,
        readonly=True
    )
    
    # 2. Stage (Many2one to the project stage line, filtered by project)
    stage_id = fields.Many2one(
        'h_jubran.project.stage.global',
        string='Stage',
        help="The specific stage of the project this purchase relates to."
    )
    
    # 3. Element (Many2one to the global element model, filtered by stage)
    element_id = fields.Many2one(
        'h_jubran.project.element.global',
        string='Element',
        help="The specific element within the stage this purchase relates to."
    )

    # 4. Substage (Many2one to the global stage model, filtered by is_sub_stage=True)
    substage_id = fields.Many2one(
        'h_jubran.project.stage.global',
        string='Substage',
        help="A granular phase within the stage."
    )
    
    # 5. Subcategory link for BOQ actual cost tracking
    subcategory_id = fields.Many2one(
        'h_jubran.master.subcategory',
        string='Sub-Category',
        required=False,
        help="Link to BOQ subcategory for automatic actual cost tracking. Must match project and subcategory code. If set, product is optional."
    )
    
    # 6. Category (from purchase request)
    category_id = fields.Many2one(
        'h_jubran.master.category',
        string='Category',
        help="Master data category from purchase request."
    )
    
    # 7. Element (from purchase request)
    master_element_id = fields.Many2one(
        'h_jubran.master.element',
        string='Element',
        domain="[('subcategory_id', '=', subcategory_id)]",
        help="Master data element from purchase request."
    )
    
    # 8. BOQ Rate (from purchase request)
    boq_rate = fields.Monetary(
        string='BOQ Rate',
        currency_field='currency_id',
        readonly=True,
        help="Rate from BOQ Summary for this category and subcategory."
    )
    
    # 9. Location (from purchase request)
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
        domain="[('usage', 'in', ['internal', 'transit'])]",
        help="Location from purchase request line."
    )
    
    # 9. Link to Purchase Request Lines
    purchase_lines = fields.Many2many(
        'h_jubran.purchase.request.line',
        relation='h_jubran_pr_purchase_order_line_rel',
        column1='purchase_order_line_id',
        column2='purchase_request_line_id',
        string='Purchase Request Lines',
        readonly=True,
        copy=False,
    )
    
    @api.constrains('product_id', 'subcategory_id')
    def _check_product_or_subcategory(self):
        """Ensure either product_id or subcategory_id is provided"""
        for line in self:
            if line.display_type:
                continue  # Skip section/note lines
            if not line.product_id and not line.subcategory_id:
                raise ValidationError(_("Either Product or Sub-Category must be provided on line: %s") % (line.name or 'Untitled'))
    
    @api.onchange('subcategory_id')
    def _onchange_subcategory_id(self):
        """When subcategory is selected, make product optional and set name from subcategory"""
        if self.subcategory_id:
            # Set name from subcategory if product is not set
            if not self.product_id:
                self.name = f"{self.subcategory_id.code} - {self.subcategory_id.name}"
            # Update category from subcategory
            self.category_id = self.subcategory_id.category_id.id
            # Clear product requirement
            self.product_id = False
        self.master_element_id = False
   
    @api.onchange('master_element_id')
    def _onchange_master_element_id(self):
        """Update subcategory and category when element changes."""
        if self.master_element_id:
            self.subcategory_id = self.master_element_id.subcategory_id.id
            self.category_id = self.master_element_id.category_id.id
   
    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        """Clear substage and element when the main stage changes."""
        self.substage_id = False
        self.element_id = False
    
    def _update_boq_actual_costs(self):
        """Update BOQ Summary Line actual costs when PO is confirmed"""
        for line in self:
            # Skip if no subcategory or project
            if not line.subcategory_id or not line.project_id:
                continue
            
            # If no product, use manual quantity/rate from line
            if not line.product_id:
                # Use manual values if product_qty and price_unit are set manually
                po_quantity = line.product_qty or 0.0
                po_rate = line.price_unit or 0.0
                po_amount = line.price_subtotal or (po_quantity * po_rate)
            else:
                # Use standard product values
                po_quantity = line.product_qty
                po_rate = line.price_unit
                po_amount = line.price_subtotal
            
            # Find matching BOQ Summary Lines: same project and subcategory
            boq_lines = self.env['h_jubran.boq.summary.line'].search([
                ('summary_id.project_id', '=', line.project_id.id),
                ('subcategory_id', '=', line.subcategory_id.id)
            ])
            
            if not boq_lines:
                continue
            
            # For each matching BOQ line, aggregate values from all PO lines with same subcategory
            for boq_line in boq_lines:
                # Get all PO lines that match this BOQ line (same project + subcategory)
                all_matching_po_lines = self.env['purchase.order.line'].search([
                    ('subcategory_id', '=', line.subcategory_id.id),
                    ('order_id.project_id', '=', line.project_id.id),
                    ('order_id.state', 'in', ['purchase', 'done']),
                    ('id', '!=', False)  # Exclude deleted lines
                ])
                
                # Calculate aggregated values: sum quantities and amounts, weighted average rate
                # Handle both product-based and manual PO lines
                total_quantity = 0.0
                total_amount = 0.0
                for po_line in all_matching_po_lines:
                    qty = po_line.product_qty or 0.0
                    amount = po_line.price_subtotal or (qty * (po_line.price_unit or 0.0))
                    total_quantity += qty
                    total_amount += amount
                
                weighted_rate = total_amount / total_quantity if total_quantity > 0 else 0.0
                
                # Update BOQ line actual values and track all PO lines
                boq_line.write({
                    'actual_quantity': total_quantity,
                    'actual_rate': weighted_rate,
                    'actual_amount': total_amount,
                    'purchase_order_line_ids': [(6, 0, all_matching_po_lines.ids)]  # Replace with all matching PO lines
                })
    
    def write(self, vals):
        """Override write to update BOQ when PO line changes"""
        result = super().write(vals)
        # Update BOQ if PO is confirmed and subcategory/project/quantities changed
        if self.order_id.state in ['purchase', 'done']:
            relevant_fields = {'subcategory_id', 'product_qty', 'price_unit', 'price_subtotal'}
            if relevant_fields.intersection(vals.keys()):
                self._update_boq_actual_costs()
        return result
    