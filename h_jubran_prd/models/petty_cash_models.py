from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PettyCash(models.Model):
    _name = 'h_jubran.petty.cash'
    _description = 'Petty Cash'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    
    custodian_id = fields.Many2one(
        'res.users',
        string='Custodian',
        required=True,
        tracking=True,
        help="Person responsible for managing the petty cash"
    )
    
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
        required=True,
        tracking=True,
        domain="[('usage', 'in', ['internal', 'transit'])]",
        help="Warehouse location for petty cash"
    )
    
    project_id = fields.Many2one(
        'h_jubran.project',
        string='Project',
        tracking=True,
        help="Associated project for this petty cash"
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        readonly=True,
        default=lambda self: self.env.company
    )
    
    date_from = fields.Date(
        string='Date From',
        required=True,
        tracking=True
    )
    
    date_to = fields.Date(
        string='Date To',
        required=True,
        tracking=True
    )
    
    amount_issued = fields.Monetary(
        string='Amount Issued',
        currency_field='currency_id',
        compute='_compute_amounts',
        store=True,
        readonly=True
    )
    
    amount_expended = fields.Monetary(
        string='Amount Expended',
        currency_field='currency_id',
        compute='_compute_amounts',
        store=True,
        readonly=True
    )
    
    balance = fields.Monetary(
        string='Balance',
        currency_field='currency_id',
        compute='_compute_amounts',
        store=True,
        readonly=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        store=True,
        readonly=True
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('request_approval', 'Request Approval'),
        ('approved', 'Approved'),
        ('done', 'Done'),
    ], string='Status', default='draft', tracking=True)
    
    journal_entry_count = fields.Integer(
        string='Journal Entries',
        compute='_compute_journal_entry_count'
    )
    
    @api.depends('issue_line_ids.move_id', 'breakdown_line_ids.move_id')
    def _compute_journal_entry_count(self):
        for record in self:
            issue_moves = record.issue_line_ids.filtered('move_id').mapped('move_id')
            breakdown_moves = record.breakdown_line_ids.filtered('move_id').mapped('move_id')
            all_moves = issue_moves | breakdown_moves
            record.journal_entry_count = len(all_moves)
    
    issue_line_ids = fields.One2many(
        'h_jubran.petty.cash.issue',
        'petty_cash_id',
        string='Issue Amount to Custodian'
    )
    
    breakdown_line_ids = fields.One2many(
        'h_jubran.petty.cash.breakdown',
        'petty_cash_id',
        string='Petty Breakdown'
    )
    
    @api.depends('issue_line_ids.amount', 'breakdown_line_ids.request_amount', 'breakdown_line_ids.amount')
    def _compute_amounts(self):
        for record in self:
            record.amount_issued = sum(record.issue_line_ids.mapped('amount'))
            # Use request_amount if set, otherwise use amount
            breakdown_amounts = []
            for line in record.breakdown_line_ids:
                breakdown_amounts.append(line.request_amount if line.request_amount else (line.amount or 0.0))
            record.amount_expended = sum(breakdown_amounts)
            record.balance = record.amount_issued - record.amount_expended
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('h_jubran.petty.cash') or _('New')
        return super().create(vals)
    
    def action_request_approval(self):
        self.write({'state': 'request_approval'})
    
    def action_approve(self):
        """Approve petty cash and create journal entries for all issue lines"""
        self.write({'state': 'approved'})
        # Create journal entries for all issue lines
        for issue_line in self.issue_line_ids:
            if not issue_line.move_id and issue_line.debit_account_id and issue_line.credit_account_id and issue_line.journal_id:
                issue_line._create_journal_entry()
    
    def action_done(self):
        self.write({'state': 'done'})
    
    def action_draft(self):
        self.write({'state': 'draft'})
    
    def action_view_journal_entries(self):
        """Open the journal entries created from issue lines and breakdown lines"""
        self.ensure_one()
        issue_moves = self.issue_line_ids.filtered('move_id').mapped('move_id')
        breakdown_moves = self.breakdown_line_ids.filtered('move_id').mapped('move_id')
        all_moves = issue_moves | breakdown_moves
        move_ids = all_moves.ids
        return {
            'name': _('Journal Entries'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', move_ids)],
            'context': {'create': False},
        }
    
    def action_view_breakdown_lines(self):
        self.ensure_one()
        return {
            'name': _('Petty Cash Breakdown'),
            'type': 'ir.actions.act_window',
            'res_model': 'h_jubran.petty.cash.breakdown',
            'view_mode': 'list,form',
            'domain': [('petty_cash_id', '=', self.id)],
            'context': {'default_petty_cash_id': self.id},
        }


class PettyCashIssue(models.Model):
    _name = 'h_jubran.petty.cash.issue'
    _description = 'Petty Cash Issue'
    _order = 'id desc'

    petty_cash_id = fields.Many2one(
        'h_jubran.petty.cash',
        string='Petty Cash',
        required=True,
        ondelete='cascade'
    )
    
    reference = fields.Char(
        string='Reference',
        help="Reference number for this issue"
    )
    
    debit_account_id = fields.Many2one(
        'account.account',
        string='Debit Account',
        domain="[('deprecated', '=', False)]",
        help="Debit account for this transaction"
    )
    
    credit_account_id = fields.Many2one(
        'account.account',
        string='Credit Account',
        domain="[('deprecated', '=', False)]",
        help="Credit account for this transaction"
    )
    
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        domain="[('type', '=', 'general')]",
        help="Journal for this transaction"
    )
    
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today
    )
    
    note = fields.Text(string='Notes')
    
    amount = fields.Monetary(
        string='Amount',
        currency_field='currency_id',
        required=True
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='petty_cash_id.currency_id',
        store=True,
        readonly=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='petty_cash_id.company_id',
        store=True,
        readonly=True
    )
    
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
        copy=False,
        help="Journal entry created when this issue is approved"
    )
    
    def write(self, vals):
        # Don't create journal entry here - it will be created when petty cash is approved
        return super().write(vals)
    
    def _create_journal_entry(self):
        """Create a draft journal entry for approved issue"""
        self.ensure_one()
        if not self.debit_account_id or not self.credit_account_id or not self.journal_id:
            raise ValidationError(_("Debit Account, Credit Account, and Journal are required to create journal entry."))
        
        move_vals = {
            'move_type': 'entry',
            'journal_id': self.journal_id.id,
            'date': self.date,
            'ref': f"Petty Cash Issue: {self.reference or self.petty_cash_id.name}",
            'state': 'draft',
            'company_id': self.company_id.id,
            'line_ids': [
                (0, 0, {
                    'account_id': self.debit_account_id.id,
                    'debit': self.amount,
                    'credit': 0.0,
                    'name': self.reference or f"Issue to {self.petty_cash_id.custodian_id.name}",
                }),
                (0, 0, {
                    'account_id': self.credit_account_id.id,
                    'debit': 0.0,
                    'credit': self.amount,
                    'name': self.reference or f"Issue to {self.petty_cash_id.custodian_id.name}",
                }),
            ],
        }
        move = self.env['account.move'].create(move_vals)
        self.move_id = move.id
        return move


class PettyCashBreakdown(models.Model):
    _name = 'h_jubran.petty.cash.breakdown'
    _description = 'Petty Cash Breakdown'
    _order = 'id desc'

    petty_cash_id = fields.Many2one(
        'h_jubran.petty.cash',
        string='Petty Cash',
        required=True,
        ondelete='cascade'
    )
    
    reference = fields.Char(
        string='Reference',
        help="Reference number for this breakdown line"
    )
    
    request_description = fields.Char(
        string='Request Description',
        required=False
    )
    
    note = fields.Text(
        string='Note',
        help="Additional notes for this breakdown line"
    )
    
    debit_account_id = fields.Many2one(
        'account.account',
        string='Debit Account',
        required=True,
        domain="[('deprecated', '=', False)]"
    )
    
    credit_account_id = fields.Many2one(
        'account.account',
        string='Credit Account',
        required=True,
        domain="[('deprecated', '=', False)]"
    )
    
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        required=True,
        domain="[('type', '=', 'general')]"
    )
    
    request_date = fields.Date(
        string='Request Date',
        required=True,
        default=fields.Date.context_today
    )
    
    request_amount = fields.Monetary(
        string='Request Amount',
        currency_field='currency_id',
        required=False,
        help="Request amount for this breakdown line"
    )
    
    category_id = fields.Many2one(
        'h_jubran.master.category',
        string='Category',
        help="Master data category for cost classification."
    )
    
    subcategory_id = fields.Many2one(
        'h_jubran.master.subcategory',
        string='Sub-Category',
        domain="[('category_id', '=', category_id)]",
        help="Master data sub-category for cost classification."
    )
    
    element_id = fields.Many2one(
        'h_jubran.master.element',
        string='Element',
        domain="[('subcategory_id', '=', subcategory_id)]",
        help="Master data element for cost classification."
    )
    
    rate = fields.Monetary(
        string='Rate',
        currency_field='currency_id',
        help="Unit rate for this line item."
    )
    
    quantity = fields.Float(
        string='Quantity',
        digits=(16, 2),
        default=1.0
    )
    
    amount = fields.Monetary(
        string='Amount',
        currency_field='currency_id',
        help="Total amount (can be manually entered or calculated from Quantity * Rate)."
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='petty_cash_id.currency_id',
        store=True,
        readonly=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='petty_cash_id.company_id',
        store=True,
        readonly=True
    )
    
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
        copy=False,
        help="Journal entry created for this breakdown line"
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    status = fields.Char(
        string='Status',
        compute='_compute_status',
        store=True,
        help="Current status of this breakdown line"
    )
    
    @api.depends('state')
    def _compute_status(self):
        for line in self:
            line.status = dict(self._fields['state'].selection).get(line.state, '')
    
    @api.model
    def create(self, vals):
        record = super().create(vals)
        # Create journal entry and update subcategory when breakdown is created
        if record.debit_account_id and record.credit_account_id and record.journal_id:
            record._create_journal_entry()
        if record.subcategory_id:
            record._update_subcategory_amounts()
        return record
    
    def write(self, vals):
        result = super().write(vals)
        # Create journal entry if not exists and accounts are set
        for record in self:
            if not record.move_id and record.debit_account_id and record.credit_account_id and record.journal_id:
                record._create_journal_entry()
            # Update subcategory if subcategory or amount changed
            if 'subcategory_id' in vals or 'amount' in vals or 'quantity' in vals or 'rate' in vals:
                if record.subcategory_id:
                    record._update_subcategory_amounts()
        return result
    
    def _create_journal_entry(self):
        """Create a journal entry for breakdown line"""
        self.ensure_one()
        if not self.debit_account_id or not self.credit_account_id or not self.journal_id:
            return False
        
        # Use amount if set, otherwise use request_amount
        amount = self.amount or self.request_amount or 0.0
        if amount <= 0:
            return False
        
        move_vals = {
            'move_type': 'entry',
            'journal_id': self.journal_id.id,
            'date': self.request_date,
            'ref': f"Petty Cash Breakdown: {self.reference or self.request_description}",
            'state': 'draft',
            'company_id': self.company_id.id,
            'line_ids': [
                (0, 0, {
                    'account_id': self.debit_account_id.id,
                    'debit': amount,
                    'credit': 0.0,
                    'name': self.reference or self.request_description,
                }),
                (0, 0, {
                    'account_id': self.credit_account_id.id,
                    'debit': 0.0,
                    'credit': amount,
                    'name': self.reference or self.request_description,
                }),
            ],
        }
        move = self.env['account.move'].create(move_vals)
        self.move_id = move.id
        return move
    
    def _update_subcategory_amounts(self):
        """Update subcategory quantity and rate similar to vendor bills"""
        self.ensure_one()
        if not self.subcategory_id:
            return
        
        # Get all petty cash breakdown lines for this subcategory
        all_breakdown_lines = self.env['h_jubran.petty.cash.breakdown'].search([
            ('subcategory_id', '=', self.subcategory_id.id),
            ('move_id', '!=', False),  # Only count lines with journal entries
        ])
        
        # Calculate total quantity and amount
        total_quantity = sum(all_breakdown_lines.mapped('quantity'))
        total_amount = sum(all_breakdown_lines.mapped('amount'))
        
        # Calculate weighted average rate
        weighted_rate = total_amount / total_quantity if total_quantity > 0 else 0.0
        
        # Update subcategory
        self.subcategory_id.write({
            'quantity': total_quantity,
            'rate': weighted_rate
        })
        
        # Update BOQ Summary Lines if project is set
        if self.petty_cash_id.project_id:
            boq_lines = self.env['h_jubran.boq.summary.line'].search([
                ('summary_id.project_id', '=', self.petty_cash_id.project_id.id),
                ('subcategory_id', '=', self.subcategory_id.id)
            ])
            
            if boq_lines:
                # Get all breakdown lines for this project + subcategory
                project_breakdown_lines = all_breakdown_lines.filtered(
                    lambda l: l.petty_cash_id.project_id.id == self.petty_cash_id.project_id.id
                )
                
                project_total_quantity = sum(project_breakdown_lines.mapped('quantity'))
                project_total_amount = sum(project_breakdown_lines.mapped('amount'))
                project_weighted_rate = project_total_amount / project_total_quantity if project_total_quantity > 0 else 0.0
                
                for boq_line in boq_lines:
                    boq_line.write({
                        'actual_quantity': project_total_quantity,
                        'actual_rate': project_weighted_rate,
                        'actual_amount': project_total_amount
                    })
    
    @api.onchange('subcategory_id')
    def _onchange_subcategory_id(self):
        if self.subcategory_id:
            self.category_id = self.subcategory_id.category_id.id
        self.element_id = False
    
    @api.onchange('element_id')
    def _onchange_element_id(self):
        if self.element_id:
            self.subcategory_id = self.element_id.subcategory_id.id
            self.category_id = self.element_id.category_id.id
    
    @api.onchange('quantity', 'rate')
    def _onchange_qty_rate(self):
        # Auto-calculate amount when quantity or rate changes, but user can still override manually
        calculated_amount = (self.quantity or 0.0) * (self.rate or 0.0)
        if calculated_amount:
            self.amount = calculated_amount
            if not self.request_amount:
                self.request_amount = calculated_amount
    
    @api.onchange('amount')
    def _onchange_amount(self):
        # Auto-set request_amount from amount if not already set
        if self.amount and not self.request_amount:
            self.request_amount = self.amount

