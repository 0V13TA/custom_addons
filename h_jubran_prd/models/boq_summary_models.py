from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HJubranBoqSummary(models.Model):
    _name = 'h_jubran.boq.summary'
    _description = 'BOQ Summary'
    _order = 'create_date desc'

    name = fields.Char(string='Summary Name', required=True)
    project_id = fields.Many2one(
        'h_jubran.project',
        string='Project',
        required=True,
        ondelete='restrict'
    )
    note = fields.Text(string='Notes / Description')
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id.id
    )
    line_ids = fields.One2many(
        'h_jubran.boq.summary.line',
        'summary_id',
        string='BOQ Lines'
    )
    scope_summary_ids = fields.One2many(
        'h_jubran.boq.summary.scope.summary',
        'summary_id',
        string='Scope Summary'
    )
    total_amount = fields.Monetary(
        string='Planned Amount',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True
    )
    total_actual_amount = fields.Monetary(
        string='Actual Amount',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True
    )

    @api.depends('line_ids.amount', 'line_ids.actual_amount')
    def _compute_totals(self):
        for summary in self:
            summary.total_amount = sum(summary.line_ids.mapped('amount'))
            summary.total_actual_amount = sum(summary.line_ids.mapped('actual_amount'))

    def _compute_scope_summary(self):
        for summary in self:
            # Delete existing scope summary records
            summary.scope_summary_ids.unlink()
            
            # Get all scopes and aggregate amounts
            all_scopes = summary.line_ids.mapped('scope')
            normalized_scopes = {}
            for scope in all_scopes:
                if scope:
                    normalized = str(scope).strip()
                    if normalized:
                        key = normalized.lower()
                        if key not in normalized_scopes:
                            normalized_scopes[key] = normalized
            
            # Create scope summary records
            scope_summary_model = self.env['h_jubran.boq.summary.scope.summary']
            for scope_name in sorted(normalized_scopes.values()):
                scope_lines = summary.line_ids.filtered(
                    lambda l: l.scope and str(l.scope).strip().lower() == scope_name.lower()
                )
                total_amount = sum(scope_lines.mapped('amount')) or 0.0
                total_actual_amount = sum(scope_lines.mapped('actual_amount')) or 0.0
                
                scope_summary_model.create({
                    'summary_id': summary.id,
                    'scope': scope_name,
                    'amount': total_amount,
                    'actual_amount': total_actual_amount,
                })

    @api.model
    def create(self, vals_list):
        records = super().create(vals_list)
        # Always compute scope summary
        for record in records:
            record._compute_scope_summary()
            record._auto_create_trees()
        return records

    def write(self, vals):
        result = super().write(vals)
        if 'line_ids' in vals:
            # Always compute scope summary when lines change
            self._compute_scope_summary()
            # Automatically update tree views when lines change
            # Skip during import to avoid blocking
            if not self.env.context.get('import_file') and not self.env.context.get('import_compat'):
                for record in self:
                    try:
                        record._auto_create_trees()
                    except Exception:
                        pass
        return result

    def _auto_create_trees(self):
        """Automatically create/update category and scope tree views"""
        for summary in self:
            # Create category tree
            category_tree_model = self.env['h_jubran.boq.summary.category.tree']
            category_tree_model.create_tree_for_summary(summary.id)
            
            # Create scope tree
            scope_tree_model = self.env['h_jubran.boq.summary.scope.tree']
            scope_tree_model.create_tree_for_summary(summary.id)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """Override to ensure scope summary is computed when form is viewed"""
        result = super().fields_view_get(view_id, view_type, toolbar, submenu)
        if view_type == 'form' and self.env.context.get('active_id'):
            record = self.browse(self.env.context['active_id'])
            if record.exists() and record.line_ids:
                # Always recompute scope summary when form is viewed
                record._compute_scope_summary()
        return result

    @api.onchange('line_ids')
    def _onchange_line_ids_scope_summary(self):
        """Compute scope summary when line_ids change"""
        self._compute_scope_summary()

    def action_refresh_scope_summary(self):
        """Button action to refresh scope summary"""
        self._compute_scope_summary()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Scope summary has been refreshed.'),
                'type': 'success',
                'sticky': False,
            }
        }

    category_count = fields.Integer(
        string='Categories',
        compute='_compute_category_count'
    )
    subcategory_count = fields.Integer(
        string='Sub-Categories',
        compute='_compute_category_count'
    )
    scope_count = fields.Integer(
        string='Scopes',
        compute='_compute_scope_count'
    )

    @api.depends('line_ids.category_id', 'line_ids.subcategory_id')
    def _compute_category_count(self):
        for summary in self:
            unique_categories = summary.line_ids.mapped('category_id')
            summary.category_count = len(unique_categories)
            unique_subcategories = summary.line_ids.mapped('subcategory_id').filtered(lambda sc: sc)
            summary.subcategory_count = len(unique_subcategories)

    @api.depends('line_ids.scope')
    def _compute_scope_count(self):
        for summary in self:
            scopes = summary.line_ids.mapped('scope')
            unique_scopes = [s for s in scopes if s]  # Filter out empty/False values
            summary.scope_count = len(set(unique_scopes))  # Get unique count

    def action_view_category_tree(self):
        self.ensure_one()
        # Create tree records for this summary
        tree_model = self.env['h_jubran.boq.summary.category.tree']
        tree_model.create_tree_for_summary(self.id)
        
        return {
            'name': _('Categories'),
            'type': 'ir.actions.act_window',
            'res_model': 'h_jubran.boq.summary.category.tree',
            'view_mode': 'list',
            'target': 'current',
            'context': {
                'default_summary_id': self.id,
                'group_by': 'category_id',
            },
            'domain': [('summary_id', '=', self.id)],
        }

    def action_view_scope_tree(self):
        self.ensure_one()
        # Create tree records for this summary
        tree_model = self.env['h_jubran.boq.summary.scope.tree']
        tree_model.create_tree_for_summary(self.id)
        
        return {
            'name': _('Scopes'),
            'type': 'ir.actions.act_window',
            'res_model': 'h_jubran.boq.summary.scope.tree',
            'view_mode': 'list',
            'target': 'current',
            'context': {
                'default_summary_id': self.id,
                'group_by': 'scope',  # Group by scope by default
            },
            'domain': [('summary_id', '=', self.id), ('is_category', '=', True)],  # Only show category nodes
        }

    def action_import_lines(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'import',
            'name': _('Import BOQ Summary Lines'),
            'params': {
                'model': 'h_jubran.boq.summary.line',
                'context': {
                    'default_summary_id': self.id,
                },
            },
        }


class HJubranBoqSummaryLine(models.Model):
    _name = 'h_jubran.boq.summary.line'
    _description = 'BOQ Summary Line'
    _order = 'sequence, id'

    summary_id = fields.Many2one(
        'h_jubran.boq.summary',
        string='BOQ Summary',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(default=10)
    number = fields.Char(string='Number')
    code = fields.Char(string='Code', required=True)
    scope = fields.Char(string='Scope', required=True)
    category_id = fields.Many2one(
        'h_jubran.master.category',
        string='Category',
        required=False,
        ondelete='restrict'
    )
    subcategory_id = fields.Many2one(
        'h_jubran.master.subcategory',
        string='Sub-Category',
        domain="[('category_id', '=', category_id)]"
    )
    element_id = fields.Many2one(
        'h_jubran.master.element',
        string='Element',
        domain="[('subcategory_id', '=', subcategory_id)]"
    )
    quantity = fields.Float(
        string='Quantity',
        digits=(16, 2)
    )
    actual_quantity = fields.Float(
        string='Actual Quantity',
        digits=(16, 2),
        readonly=True,
        help="Automatically updated from Purchase Orders linked to this subcategory"
    )
    rate = fields.Monetary(
        string='Rate',
        currency_field='currency_id'
    )
    actual_rate = fields.Monetary(
        string='Actual Rate',
        currency_field='currency_id',
        readonly=True,
        help="Automatically updated from Purchase Orders linked to this subcategory"
    )
    amount = fields.Monetary(
        string='Amount',
        currency_field='currency_id'
    )
    actual_amount = fields.Monetary(
        string='Actual Amount',
        currency_field='currency_id',
        readonly=True,
        help="Automatically updated from Purchase Orders linked to this subcategory"
    )
    purchase_order_line_ids = fields.Many2many(
        'purchase.order.line',
        string='Linked Purchase Order Lines',
        readonly=True,
        help="Purchase Order Lines that have updated this BOQ line's actual costs"
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='summary_id.currency_id',
        store=True,
        readonly=True
    )
    sale_order_line_ids = fields.One2many(
        'sale.order.line',
        'boq_summary_line_id',
        string='Linked Sales Lines'
    )
    invoice_line_ids = fields.One2many(
        'account.move.line',
        'boq_summary_line_id',
        string='Linked Invoice Lines'
    )

    _sql_constraints = [
        (
            'summary_code_unique',
            'unique(summary_id, code)',
            'Code must be unique per BOQ summary.'
        ),
    ]

    @api.constrains('amount', 'actual_amount')
    def _check_amounts(self):
        for line in self:
            if line.amount and line.amount < 0:
                raise ValidationError(_('Amount cannot be negative.'))
            if line.actual_amount and line.actual_amount < 0:
                raise ValidationError(_('Actual Amount cannot be negative.'))

    @api.onchange('subcategory_id')
    def _onchange_subcategory_id(self):
        for line in self:
            if line.subcategory_id:
                line.category_id = line.subcategory_id.category_id.id
            elif line.category_id and not line.subcategory_id:
                # keep existing category selection
                continue

    @api.onchange('element_id')
    def _onchange_element_id(self):
        for line in self:
            if line.element_id:
                line.subcategory_id = line.element_id.subcategory_id.id
                line.category_id = line.element_id.category_id.id

    @api.model
    def create(self, vals_list):
        """Override create to trigger tree creation on parent summary"""
        # Handle both single dict and list of dicts (Odoo 18 compatibility)
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
        
        records = super().create(vals_list)
        
        # Trigger tree creation and scope summary for all affected summaries
        summaries = records.mapped('summary_id')
        for summary in summaries:
            try:
                # Always compute scope summary (it's fast)
                summary._compute_scope_summary()
                # Only create trees if not in import mode (to avoid blocking)
                if not self.env.context.get('import_file') and not self.env.context.get('import_compat'):
                    summary._auto_create_trees()
            except Exception:
                # Silently fail to avoid blocking imports
                pass
        
        # Recompute boq_rate in purchase request lines when new BOQ line is created
        self._recompute_pr_boq_rates(records)
        
        return records

    def write(self, vals):
        """Override write to trigger tree creation on parent summary"""
        # Get summaries before write
        summaries = self.mapped('summary_id')
        result = super().write(vals)
        # Trigger scope summary and tree creation for all affected summaries
        summaries |= self.mapped('summary_id')
        for summary in summaries:
            try:
                # Always compute scope summary (it's fast)
                summary._compute_scope_summary()
                # Only create trees if not in import mode (to avoid blocking)
                if not self.env.context.get('import_file') and not self.env.context.get('import_compat'):
                    summary._auto_create_trees()
            except Exception:
                pass
        
        # Recompute boq_rate in purchase request lines if rate or subcategory changed
        if 'rate' in vals or 'subcategory_id' in vals or 'category_id' in vals:
            self._recompute_pr_boq_rates(self)
        
        return result
    
    def _recompute_pr_boq_rates(self, boq_lines):
        """Recompute boq_rate in purchase request lines for given BOQ summary lines"""
        if not boq_lines:
            return
        
        # Get all affected subcategories
        subcategory_ids = boq_lines.mapped('subcategory_id').ids
        if not subcategory_ids:
            return
        
        # Find all purchase request lines with matching subcategories
        pr_lines = self.env['h_jubran.purchase.request.line'].search([
            ('subcategory_id', 'in', subcategory_ids)
        ])
        
        if pr_lines:
            # Recompute boq_rate for these lines
            pr_lines._compute_boq_rate()

    def unlink(self):
        """Override unlink to trigger tree creation on parent summary"""
        summaries = self.mapped('summary_id')
        result = super().unlink()
        # Trigger tree creation for all affected summaries
        for summary in summaries:
            try:
                summary._auto_create_trees()
                summary._compute_scope_summary()
            except Exception:
                pass
        return result


class HJubranBoqSummaryCategoryTree(models.Model):
    _name = 'h_jubran.boq.summary.category.tree'
    _description = 'BOQ Summary Category Tree View'
    _order = 'parent_id, sequence, id'
    _parent_name = 'parent_id'
    _parent_store = True

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    summary_id = fields.Many2one(
        'h_jubran.boq.summary',
        string='BOQ Summary',
        required=True,
        ondelete='cascade',
        index=True
    )
    category_id = fields.Many2one(
        'h_jubran.master.category',
        string='Category',
        ondelete='cascade'
    )
    subcategory_id = fields.Many2one(
        'h_jubran.master.subcategory',
        string='Sub-Category',
        ondelete='cascade'
    )
    parent_id = fields.Many2one(
        'h_jubran.boq.summary.category.tree',
        string='Parent',
        ondelete='cascade',
        index=True
    )
    parent_path = fields.Char(index=True)
    sequence = fields.Integer(default=10)
    is_category = fields.Boolean(string='Is Category', default=False)
    is_subcategory = fields.Boolean(string='Is Sub-Category', default=False)
    
    # Fields from BOQ Summary Lines
    quantity = fields.Float(
        string='Quantity',
        digits=(16, 2),
        compute='_compute_amounts',
        store=True,
        readonly=False
    )
    actual_quantity = fields.Float(
        string='Actual Quantity',
        digits=(16, 2),
        compute='_compute_amounts',
        store=True,
        readonly=False
    )
    rate = fields.Monetary(
        string='Rate',
        currency_field='currency_id',
        compute='_compute_amounts',
        store=True,
        readonly=False
    )
    actual_rate = fields.Monetary(
        string='Actual Rate',
        currency_field='currency_id',
        compute='_compute_amounts',
        store=True,
        readonly=False
    )
    amount = fields.Monetary(
        string='Amount',
        currency_field='currency_id',
        compute='_compute_amounts',
        store=True,
        readonly=False
    )
    actual_amount = fields.Monetary(
        string='Actual Amount',
        currency_field='currency_id',
        compute='_compute_amounts',
        store=True,
        readonly=False
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='summary_id.currency_id',
        store=True,
        readonly=True
    )

    @api.depends('category_id', 'subcategory_id', 'is_category', 'is_subcategory', 'category_id.code', 'category_id.name', 'subcategory_id.code', 'subcategory_id.name')
    def _compute_name(self):
        for record in self:
            if record.is_subcategory and record.subcategory_id:
                record.name = f"{record.subcategory_id.code} - {record.subcategory_id.name}"
            else:
                record.name = ''

    @api.depends('category_id', 'subcategory_id', 'summary_id', 'summary_id.line_ids', 'summary_id.line_ids.subcategory_id', 
                 'summary_id.line_ids.quantity', 'summary_id.line_ids.actual_quantity', 
                 'summary_id.line_ids.rate', 'summary_id.line_ids.actual_rate',
                 'summary_id.line_ids.amount', 'summary_id.line_ids.actual_amount')
    def _compute_amounts(self):
        for record in self:
            if record.is_subcategory and record.subcategory_id:
                # Sub-categories show values from BOQ lines
                lines = record.summary_id.line_ids.filtered(
                    lambda l: l.subcategory_id and l.subcategory_id.id == record.subcategory_id.id
                )
                record.quantity = sum(lines.mapped('quantity')) or 0.0
                record.actual_quantity = sum(lines.mapped('actual_quantity')) or 0.0
                record.rate = sum(lines.mapped('rate')) or 0.0
                record.actual_rate = sum(lines.mapped('actual_rate')) or 0.0
                record.amount = sum(lines.mapped('amount')) or 0.0
                record.actual_amount = sum(lines.mapped('actual_amount')) or 0.0
            else:
                record.quantity = 0.0
                record.actual_quantity = 0.0
                record.rate = 0.0
                record.actual_rate = 0.0
                record.amount = 0.0
                record.actual_amount = 0.0

    def write(self, vals):
        """Override write to update underlying BOQ lines when tree view fields are edited"""
        # If editing quantity, rate, or amount fields, update the underlying BOQ lines FIRST
        # This prevents the computed field from overwriting the values
        editable_fields = {'quantity', 'actual_quantity', 'rate', 'actual_rate', 'amount', 'actual_amount'}
        if editable_fields.intersection(vals.keys()):
            # Create a copy of vals without computed fields to avoid recomputation issues
            vals_to_write = vals.copy()
            computed_fields_to_remove = editable_fields.intersection(vals.keys())
            for field in computed_fields_to_remove:
                vals_to_write.pop(field, None)
            
            for record in self:
                if record.is_subcategory and record.subcategory_id:
                    # Get all BOQ lines for this subcategory
                    boq_lines = record.summary_id.line_ids.filtered(
                        lambda l: l.subcategory_id and l.subcategory_id.id == record.subcategory_id.id
                    )
                    # If no BOQ lines exist, create one
                    if not boq_lines:
                        # Get a default scope from other BOQ lines in the summary, or use a default
                        default_scope = 'General'
                        existing_scopes = record.summary_id.line_ids.mapped('scope')
                        if existing_scopes:
                            # Use the most common scope, or first one
                            default_scope = existing_scopes[0] if existing_scopes else 'General'
                        
                        # Create a new BOQ line for this subcategory
                        boq_line_vals = {
                            'summary_id': record.summary_id.id,
                            'subcategory_id': record.subcategory_id.id,
                            'category_id': record.subcategory_id.category_id.id if record.subcategory_id.category_id else False,
                            'code': record.subcategory_id.code or f'BOQ-{record.subcategory_id.id}',
                            'scope': default_scope,
                        }
                        boq_line = self.env['h_jubran.boq.summary.line'].create(boq_line_vals)
                        boq_lines = boq_line
                    
                    if boq_lines:
                        # If there's only one line, update it directly
                        if len(boq_lines) == 1:
                            line_vals = {}
                            if 'quantity' in vals:
                                line_vals['quantity'] = vals['quantity']
                            # Don't update quantity if only rate is being updated - preserve existing value
                            if 'actual_quantity' in vals:
                                line_vals['actual_quantity'] = vals['actual_quantity']
                            # Don't update actual_quantity if only actual_rate is being updated - preserve existing value
                            if 'rate' in vals:
                                line_vals['rate'] = vals['rate']
                                # If quantity exists, recalculate amount
                                # Use the new rate value if quantity is also being updated, otherwise use existing quantity
                                qty_to_use = vals.get('quantity', boq_lines[0].quantity) or 0.0
                                if qty_to_use:
                                    line_vals['amount'] = qty_to_use * vals['rate']
                                elif 'quantity' in vals:
                                    # If quantity is being set but is 0, still set amount to 0
                                    line_vals['amount'] = 0.0
                            if 'actual_rate' in vals:
                                line_vals['actual_rate'] = vals['actual_rate']
                                # If actual_quantity exists, recalculate actual_amount
                                if boq_lines[0].actual_quantity:
                                    line_vals['actual_amount'] = boq_lines[0].actual_quantity * vals['actual_rate']
                            if 'amount' in vals:
                                line_vals['amount'] = vals['amount']
                            elif 'quantity' in vals and 'rate' in vals:
                                # If both quantity and rate are being updated, calculate amount
                                line_vals['amount'] = vals['quantity'] * vals['rate']
                            elif 'quantity' in vals and boq_lines[0].rate:
                                # If only quantity is being updated and rate exists, recalculate amount
                                line_vals['amount'] = vals['quantity'] * boq_lines[0].rate
                            if 'actual_amount' in vals:
                                line_vals['actual_amount'] = vals['actual_amount']
                            elif 'actual_quantity' in vals and 'actual_rate' in vals:
                                # If both actual_quantity and actual_rate are being updated, calculate actual_amount
                                line_vals['actual_amount'] = vals['actual_quantity'] * vals['actual_rate']
                            elif 'actual_quantity' in vals and boq_lines[0].actual_rate:
                                # If only actual_quantity is being updated and actual_rate exists, recalculate actual_amount
                                line_vals['actual_amount'] = vals['actual_quantity'] * boq_lines[0].actual_rate
                            if line_vals:
                                # Update BOQ lines first, before super().write() triggers recomputation
                                boq_lines.write(line_vals)
                        # If multiple lines, update each line individually to preserve quantities
                        else:
                            if 'rate' in vals:
                                # Update rate for all lines, preserving their quantities and recalculating amounts
                                for line in boq_lines:
                                    line_vals = {'rate': vals['rate']}
                                    # Use new quantity if being updated, otherwise use existing
                                    qty_to_use = vals.get('quantity', line.quantity) or 0.0
                                    if qty_to_use:
                                        line_vals['amount'] = qty_to_use * vals['rate']
                                    line.write(line_vals)
                            if 'actual_rate' in vals:
                                # Update actual_rate for all lines, preserving their actual_quantities and recalculating actual_amounts
                                for line in boq_lines:
                                    line_vals = {'actual_rate': vals['actual_rate']}
                                    # Use new actual_quantity if being updated, otherwise use existing
                                    qty_to_use = vals.get('actual_quantity', line.actual_quantity) or 0.0
                                    if qty_to_use:
                                        line_vals['actual_amount'] = qty_to_use * vals['actual_rate']
                                    line.write(line_vals)
                            if 'quantity' in vals:
                                # Distribute quantity proportionally
                                qty_per_line = vals['quantity'] / len(boq_lines)
                                for line in boq_lines:
                                    line_vals = {'quantity': qty_per_line}
                                    # Use new rate if being updated, otherwise use existing
                                    rate_to_use = vals.get('rate', line.rate) or 0.0
                                    if rate_to_use:
                                        line_vals['amount'] = qty_per_line * rate_to_use
                                    line.write(line_vals)
                            if 'actual_quantity' in vals:
                                # Distribute actual_quantity proportionally
                                qty_per_line = vals['actual_quantity'] / len(boq_lines)
                                for line in boq_lines:
                                    line_vals = {'actual_quantity': qty_per_line}
                                    # Use new actual_rate if being updated, otherwise use existing
                                    rate_to_use = vals.get('actual_rate', line.actual_rate) or 0.0
                                    if rate_to_use:
                                        line_vals['actual_amount'] = qty_per_line * rate_to_use
                                    line.write(line_vals)
                            if 'amount' in vals:
                                # Distribute amount proportionally
                                for line in boq_lines:
                                    line.write({'amount': vals['amount'] / len(boq_lines)})
                            if 'actual_amount' in vals:
                                # Distribute actual_amount proportionally
                                for line in boq_lines:
                                    line.write({'actual_amount': vals['actual_amount'] / len(boq_lines)})
            
            # Now call super().write() with vals that exclude computed fields
            # The computed fields will be automatically recomputed by Odoo's dependency system
            # when the BOQ lines are updated, so we don't need to manually trigger recomputation
            result = super().write(vals_to_write)
        else:
            result = super().write(vals)
        
        return result

    @api.model
    def create(self, vals_list):
        """Override create to ensure name is computed"""
        records = super().create(vals_list)
        # Trigger computation of name field
        records._compute_name()
        return records

    @api.model
    def create_tree_for_summary(self, summary_id):
        """Create tree records for a BOQ Summary - Only subcategories"""
        summary = self.env['h_jubran.boq.summary'].browse(summary_id)
        if not summary.exists():
            return
        
        # Delete existing tree records for this summary
        self.search([('summary_id', '=', summary_id)]).unlink()
        
        # Get all unique categories from BOQ Summary Lines
        unique_categories = summary.line_ids.mapped('category_id').filtered(lambda c: c)
        
        tree_records = []
        for category in unique_categories:
            # Create sub-category nodes for all master sub-categories under this category
            subcategories = category.subcategory_ids
            if not subcategories:
                # If no sub-categories exist, skip to next category
                continue

            for subcat in subcategories:
                subcat_node = self.create({
                    'summary_id': summary_id,
                    'category_id': category.id,
                    'subcategory_id': subcat.id,
                    'is_subcategory': True,
                    'parent_id': False,  # No parent, just flat list of subcategories
                    'sequence': subcat.id,
                })
                tree_records.append(subcat_node)
        
        return tree_records


class HJubranBoqSummaryScopeTree(models.Model):
    _name = 'h_jubran.boq.summary.scope.tree'
    _description = 'BOQ Summary Scope Tree View'
    _order = 'parent_id, sequence, id'
    _parent_name = 'parent_id'
    _parent_store = True

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    summary_id = fields.Many2one(
        'h_jubran.boq.summary',
        string='BOQ Summary',
        required=True,
        ondelete='cascade',
        index=True
    )
    scope = fields.Char(string='Scope')
    code = fields.Char(string='Code', compute='_compute_code', store=True)
    category_id = fields.Many2one(
        'h_jubran.master.category',
        string='Category',
        ondelete='cascade'
    )
    parent_id = fields.Many2one(
        'h_jubran.boq.summary.scope.tree',
        string='Parent',
        ondelete='cascade',
        index=True
    )
    parent_path = fields.Char(index=True)
    sequence = fields.Integer(default=10)
    is_scope = fields.Boolean(string='Is Scope', default=False)
    is_category = fields.Boolean(string='Is Category', default=False)
    
    # Fields from BOQ Summary Lines
    quantity = fields.Float(
        string='Quantity',
        digits=(16, 2),
        compute='_compute_amounts',
        store=True,
        readonly=False
    )
    actual_quantity = fields.Float(
        string='Actual Quantity',
        digits=(16, 2),
        compute='_compute_amounts',
        store=True,
        readonly=False
    )
    rate = fields.Monetary(
        string='Rate',
        currency_field='currency_id',
        compute='_compute_amounts',
        store=True,
        readonly=False
    )
    actual_rate = fields.Monetary(
        string='Actual Rate',
        currency_field='currency_id',
        compute='_compute_amounts',
        store=True,
        readonly=False
    )
    amount = fields.Monetary(
        string='Amount',
        currency_field='currency_id',
        compute='_compute_amounts',
        store=True,
        readonly=False
    )
    actual_amount = fields.Monetary(
        string='Actual Amount',
        currency_field='currency_id',
        compute='_compute_amounts',
        store=True,
        readonly=False
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='summary_id.currency_id',
        store=True,
        readonly=True
    )

    @api.depends('scope', 'category_id', 'is_scope', 'is_category', 'category_id.code', 'category_id.name')
    def _compute_name(self):
        for record in self:
            if record.is_category and record.category_id:
                record.name = f"{record.category_id.code} - {record.category_id.name}"
            else:
                record.name = ''

    @api.depends('scope', 'category_id', 'summary_id', 'summary_id.line_ids', 
                 'summary_id.line_ids.scope', 'summary_id.line_ids.category_id',
                 'summary_id.line_ids.code')
    def _compute_code(self):
        for record in self:
            if record.is_category and record.category_id and record.scope:
                # Category: get codes from BOQ lines matching this scope and category
                lines = record.summary_id.line_ids.filtered(
                    lambda l: l.scope and str(l.scope).strip() == str(record.scope).strip() and 
                             l.category_id and l.category_id.id == record.category_id.id
                )
                codes = lines.mapped('code')
                record.code = ', '.join([c for c in codes if c]) if codes else ''
            else:
                record.code = ''

    @api.depends('scope', 'category_id', 'summary_id', 'summary_id.line_ids', 
                 'summary_id.line_ids.scope', 'summary_id.line_ids.category_id',
                 'summary_id.line_ids.quantity', 'summary_id.line_ids.actual_quantity', 
                 'summary_id.line_ids.rate', 'summary_id.line_ids.actual_rate',
                 'summary_id.line_ids.amount', 'summary_id.line_ids.actual_amount')
    def _compute_amounts(self):
        for record in self:
            if record.is_category and record.category_id and record.scope:
                # Category: sum from BOQ lines matching this scope and category
                lines = record.summary_id.line_ids.filtered(
                    lambda l: l.scope and str(l.scope).strip() == str(record.scope).strip() and 
                             l.category_id and l.category_id.id == record.category_id.id
                )
                record.quantity = sum(lines.mapped('quantity')) or 0.0
                record.actual_quantity = sum(lines.mapped('actual_quantity')) or 0.0
                record.rate = sum(lines.mapped('rate')) or 0.0
                record.actual_rate = sum(lines.mapped('actual_rate')) or 0.0
                record.amount = sum(lines.mapped('amount')) or 0.0
                record.actual_amount = sum(lines.mapped('actual_amount')) or 0.0
            else:
                record.quantity = 0.0
                record.actual_quantity = 0.0
                record.rate = 0.0
                record.actual_rate = 0.0
                record.amount = 0.0
                record.actual_amount = 0.0

    def write(self, vals):
        """Override write to update underlying BOQ lines when tree view fields are edited"""
        result = super().write(vals)
        
        # If editing quantity, rate, or amount fields, update the underlying BOQ lines
        editable_fields = {'quantity', 'actual_quantity', 'rate', 'actual_rate', 'amount', 'actual_amount'}
        if editable_fields.intersection(vals.keys()):
            for record in self:
                if record.is_category and record.category_id and record.scope:
                    # Get all BOQ lines for this scope and category
                    boq_lines = record.summary_id.line_ids.filtered(
                        lambda l: l.scope and str(l.scope).strip() == str(record.scope).strip() and 
                                 l.category_id and l.category_id.id == record.category_id.id
                    )
                    if boq_lines:
                        # If there's only one line, update it directly
                        if len(boq_lines) == 1:
                            line_vals = {}
                            if 'quantity' in vals:
                                line_vals['quantity'] = vals['quantity']
                            if 'actual_quantity' in vals:
                                line_vals['actual_quantity'] = vals['actual_quantity']
                            if 'rate' in vals:
                                line_vals['rate'] = vals['rate']
                            if 'actual_rate' in vals:
                                line_vals['actual_rate'] = vals['actual_rate']
                            if 'amount' in vals:
                                line_vals['amount'] = vals['amount']
                            if 'actual_amount' in vals:
                                line_vals['actual_amount'] = vals['actual_amount']
                            if line_vals:
                                boq_lines.write(line_vals)
                        # If multiple lines, distribute proportionally
                        else:
                            line_vals = {}
                            if 'quantity' in vals:
                                line_vals['quantity'] = vals['quantity'] / len(boq_lines)
                            if 'actual_quantity' in vals:
                                line_vals['actual_quantity'] = vals['actual_quantity'] / len(boq_lines)
                            if 'rate' in vals:
                                line_vals['rate'] = vals['rate']
                            if 'actual_rate' in vals:
                                line_vals['actual_rate'] = vals['actual_rate']
                            if 'amount' in vals:
                                if 'quantity' in vals and 'rate' in vals:
                                    line_vals['amount'] = (vals['quantity'] / len(boq_lines)) * vals['rate']
                                else:
                                    line_vals['amount'] = vals['amount'] / len(boq_lines)
                            if 'actual_amount' in vals:
                                if 'actual_quantity' in vals and 'actual_rate' in vals:
                                    line_vals['actual_amount'] = (vals['actual_quantity'] / len(boq_lines)) * vals['actual_rate']
                                else:
                                    line_vals['actual_amount'] = vals['actual_amount'] / len(boq_lines)
                            if line_vals:
                                # Update BOQ lines first, before super().write() triggers recomputation
                                boq_lines.write(line_vals)
            
            # Now call super().write() with vals that exclude computed fields
            # This will trigger recomputation which will read the updated BOQ line values
            result = super().write(vals_to_write)
        else:
            result = super().write(vals)
        
        return result

    @api.model
    def create(self, vals_list):
        """Override create to ensure name is computed"""
        records = super().create(vals_list)
        # Trigger computation of name field
        records._compute_name()
        return records

    @api.model
    def create_tree_for_summary(self, summary_id):
        """Create tree records for a BOQ Summary - Only Category nodes, grouped by scope"""
        summary = self.env['h_jubran.boq.summary'].browse(summary_id)
        if not summary.exists():
            return
        
        # Delete existing tree records for this summary
        self.search([('summary_id', '=', summary_id)]).unlink()
        
        # Get all scopes from BOQ Summary Lines, normalize them (strip whitespace, case-insensitive)
        all_scopes = summary.line_ids.mapped('scope')
        # Normalize scope names (strip whitespace, convert to string, lowercase for comparison)
        normalized_scopes = {}
        for scope in all_scopes:
            if scope:
                normalized = str(scope).strip()
                if normalized:
                    # Use lowercase normalized name as key to ensure uniqueness
                    key = normalized.lower()
                    if key not in normalized_scopes:
                        normalized_scopes[key] = normalized  # Store original with proper case
        
        tree_records = []
        # Sort by original scope name (not the key)
        for scope_name in sorted(normalized_scopes.values()):
            # Get unique categories for this scope (match by normalized scope name - case insensitive)
            scope_lines = summary.line_ids.filtered(
                lambda l: l.scope and str(l.scope).strip().lower() == scope_name.lower()
            )
            unique_categories = scope_lines.mapped('category_id').filtered(lambda c: c)
            
            # Create only category nodes (no scope parent nodes)
            for category in unique_categories:
                category_node = self.create({
                    'summary_id': summary_id,
                    'scope': scope_name,  # Store scope for grouping
                    'category_id': category.id,
                    'is_category': True,
                    'is_scope': False,
                    'parent_id': False,  # No parent - will be grouped by scope field
                    'sequence': category.id,
                })
                tree_records.append(category_node)
        
        return tree_records


class HJubranBoqSummaryScopeSummary(models.Model):
    _name = 'h_jubran.boq.summary.scope.summary'
    _description = 'BOQ Summary Scope Summary'
    _order = 'scope'

    summary_id = fields.Many2one(
        'h_jubran.boq.summary',
        string='BOQ Summary',
        required=True,
        ondelete='cascade',
        index=True
    )
    scope = fields.Char(string='Scope', required=True)
    amount = fields.Monetary(
        string='Amount',
        currency_field='currency_id'
    )
    actual_amount = fields.Monetary(
        string='Actual Amount',
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='summary_id.currency_id',
        store=True,
        readonly=True
    )

    @api.model
    def create(self, vals_list):
        """Override create to set summary_id from context if not provided"""
        for vals in vals_list:
            if 'summary_id' not in vals and self.env.context.get('default_summary_id'):
                vals['summary_id'] = self.env.context['default_summary_id']
        return super().create(vals_list)


