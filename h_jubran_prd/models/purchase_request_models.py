# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError, AccessError

_STATES = [
    ("draft", "Draft"),
    ("to_approve_1", "To Approve (Level 1)"),
    ("to_approve_2", "To Approve (Level 2)"),
    ("approved", "Approved"),
    ("in_progress", "In progress"),
    ("done", "Done"),
    ("rejected", "Rejected"),
]


class PurchaseRequest(models.Model):
    _name = "h_jubran.purchase.request"
    _description = "Purchase Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    @api.model
    def _get_default_name(self):
        return self.env["ir.sequence"].next_by_code("h_jubran.purchase.request")

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ("to_approve_1", "to_approve_2", "approved", "rejected", "in_progress", "done"):
                rec.is_editable = False
            else:
                rec.is_editable = True

    name = fields.Char(
        string="Request Reference",
        required=True,
        default=lambda self: _("New"),
        tracking=True,
    )
    origin = fields.Char(string="Source Document")
    date_start = fields.Date(
        string="Creation date",
        help="Date when the user initiated the request.",
        default=fields.Date.context_today,
        tracking=True,
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        required=True,
        copy=False,
        tracking=True,
        default=_get_default_requested_by,
        index=True,
    )
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        string="Approver",
        tracking=True,
        index=True,
    )
    approver_1_id = fields.Many2one(
        comodel_name="res.users",
        string="Approver 1",
        tracking=True,
        index=True,
        help="First level approver for this purchase request."
    )
    approver_2_id = fields.Many2one(
        comodel_name="res.users",
        string="Approver 2",
        tracking=True,
        index=True,
        help="Second level (final) approver for this purchase request."
    )
    approved_by_1_id = fields.Many2one(
        comodel_name="res.users",
        string="Approved By (Level 1)",
        readonly=True,
        tracking=True,
        help="User who approved at level 1."
    )
    approved_by_2_id = fields.Many2one(
        comodel_name="res.users",
        string="Approved By (Level 2)",
        readonly=True,
        tracking=True,
        help="User who approved at level 2 (final approval)."
    )
    approval_date_1 = fields.Datetime(
        string="Approval Date (Level 1)",
        readonly=True,
        tracking=True,
    )
    approval_date_2 = fields.Datetime(
        string="Approval Date (Level 2)",
        readonly=True,
        tracking=True,
    )
    description = fields.Text()
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=False,
        default=lambda self: self.env.company,
        tracking=True,
    )
    line_ids = fields.One2many(
        comodel_name="h_jubran.purchase.request.line",
        inverse_name="request_id",
        string="Products to Purchase",
        readonly=False,
        copy=True,
        tracking=True,
    )
    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        tracking=True,
        required=True,
        copy=False,
        default="draft",
    )
    is_editable = fields.Boolean(compute="_compute_is_editable", readonly=True)
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    
    # Procurement Group field
    group_id = fields.Many2one(
        comodel_name="procurement.group",
        string="Procurement Group",
        copy=False,
        index=True,
        help="Procurement group for tracking and grouping related procurements."
    )
    
    # Custom fields
    project_id = fields.Many2one(
        'h_jubran.project',
        string='Project',
        required=False,
        tracking=True,
        help="Link the Purchase Request to a specific custom project for cost tracking."
    )
    project_site = fields.Many2one(
        'stock.location',
        string='Project Site (Location)',
        readonly=False,
        store=True,
        help="Site/Location of the linked project."
    )

    @api.onchange('project_id')
    def _onchange_project_id_site(self):
        """Auto-populate the project_site from the selected project."""
        if self.project_id:
            self.project_site = self.project_id.site
        else:
            self.project_site = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self._get_default_name()
        return super().create(vals_list)

    def _can_be_deleted(self):
        self.ensure_one()
        return self.state == "draft"

    def unlink(self):
        for request in self:
            if not request._can_be_deleted():
                raise UserError(
                    _("You cannot delete a purchase request which is not draft.")
                )
        return super().unlink()

    def _check_approval_rights(self, level):
        """Check if current user has approval rights for the specified level."""
        self.ensure_one()
        user = self.env.user
        
        if level == 1:
            # Check if user is in Approval 1 group or is the assigned approver 1
            has_group = user.has_group('h_jubran_prd.group_purchase_request_approver_1')
            is_approver = self.approver_1_id == user if self.approver_1_id else False
            return has_group or is_approver
        elif level == 2:
            # Check if user is in Approval 2 group or is the assigned approver 2
            has_group = user.has_group('h_jubran_prd.group_purchase_request_approver_2')
            is_approver = self.approver_2_id == user if self.approver_2_id else False
            return has_group or is_approver
        return False

    def button_draft(self):
        return self.write({"state": "draft"})

    def button_to_approve(self):
        """Submit for first level approval."""
        for rec in self:
            if not rec.approver_1_id:
                raise UserError(_("Please assign an Approver 1 before submitting for approval."))
            if not rec.approver_2_id:
                raise UserError(_("Please assign an Approver 2 before submitting for approval."))
        return self.write({"state": "to_approve_1"})

    def button_approved_1(self):
        """First level approval."""
        for rec in self:
            if not rec._check_approval_rights(1):
                raise UserError(_("You do not have permission to approve at Level 1."))
            if rec.state != "to_approve_1":
                raise UserError(_("This request is not pending Level 1 approval."))
            # Always go to to_approve_2 after Level 1 approval
            rec.write({
                "state": "to_approve_2",
                "approved_by_1_id": self.env.user.id,
                "approval_date_1": fields.Datetime.now(),
            })
        return True

    def button_approved_2(self):
        """Second level (final) approval."""
        for rec in self:
            if not rec._check_approval_rights(2):
                raise UserError(_("You do not have permission to approve at Level 2."))
            if rec.state != "to_approve_2":
                raise UserError(_("This request is not pending Level 2 approval."))
            rec.write({
                "state": "approved",
                "approved_by_2_id": self.env.user.id,
                "approval_date_2": fields.Datetime.now(),
            })
        return True

    def button_approved(self):
        """Legacy method - redirects to appropriate approval level."""
        for rec in self:
            if rec.state == "to_approve_1":
                return rec.button_approved_1()
            elif rec.state == "to_approve_2":
                return rec.button_approved_2()
            else:
                return rec.write({"state": "approved"})

    def button_rejected(self):
        """Reject the purchase request."""
        for rec in self:
            # Only allow rejection if in approval states
            if rec.state not in ("to_approve_1", "to_approve_2"):
                raise UserError(_("You can only reject requests that are pending approval."))
        return self.write({"state": "rejected"})

    def button_in_progress(self):
        return self.write({"state": "in_progress"})

    def button_done(self):
        return self.write({"state": "done"})
    
    def action_make_purchase_order(self):
        """Open wizard to create purchase order from purchase request"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Make Purchase Order',
            'res_model': 'h_jubran.pr.make.purchase.order',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_item_ids': [(0, 0, {
                    'line_id': line.id,
                    'product_id': line.product_id.id if line.product_id else False,
                    'name': line.name or '',
                    'product_qty': line.pending_qty_to_receive,
                    'product_uom_id': line.product_uom_id.id if line.product_uom_id else False,
                }) for line in self.line_ids if line.pending_qty_to_receive > 0]
            }
        }
    
    @api.depends('line_ids')
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)
    
    line_count = fields.Integer(string="Lines", compute="_compute_line_count")
    
    @api.depends()
    def _compute_used_in_confirmed_po(self):
        """Check if this Purchase Request has been used in any confirmed Purchase Order"""
        # Get all PRs that have been used in confirmed POs
        used_pr_ids = self.env['purchase.order'].search([
            ('state', 'in', ['purchase', 'done']),
            ('auto_complete_pr_id', '!=', False)
        ]).mapped('auto_complete_pr_id').ids
        
        for rec in self:
            rec.used_in_confirmed_po = rec.id in used_pr_ids
    
    used_in_confirmed_po = fields.Boolean(
        string='Used in Confirmed PO',
        compute='_compute_used_in_confirmed_po',
        store=True,
        help="True if this Purchase Request has been used in a confirmed Purchase Order"
    )
    
    @api.model
    def _search_not_used_in_confirmed_po(self, operator, value):
        """Search domain for Purchase Requests not used in confirmed POs"""
        if operator == '=' and value is False:
            # Find PRs that are NOT used in confirmed POs
            # Get all PRs that have lines linked to confirmed PO lines
            used_pr_ids = self.env['purchase.order.line'].search([
                ('order_id.state', 'in', ['purchase', 'done']),
                ('purchase_lines', '!=', False)
            ]).mapped('purchase_lines.request_id').ids
            
            # Return domain to exclude these PRs
            return [('id', 'not in', used_pr_ids)]
        return []


class PurchaseRequestLine(models.Model):
    _name = "h_jubran.purchase.request.line"
    _description = "Purchase Request Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(string="Description", tracking=True)
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="UoM",
        tracking=True,
        domain="[('category_id', '=', product_uom_category_id)]",
    )
    product_uom_category_id = fields.Many2one(related="product_id.uom_id.category_id")
    product_qty = fields.Float(
        string="Quantity", tracking=True, digits="Product Unit of Measure"
    )
    request_id = fields.Many2one(
        comodel_name="h_jubran.purchase.request",
        string="Purchase Request",
        ondelete="cascade",
        readonly=True,
        index=True,
        auto_join=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="request_id.company_id",
        string="Company",
        store=True,
        index=True,
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        related="request_id.requested_by",
        string="Requested by",
        store=True,
    )
    date_required = fields.Date(
        string="Request Date",
        required=True,
        tracking=True,
        default=fields.Date.context_today,
    )
    cancelled = fields.Boolean(readonly=True, default=False, copy=False)
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        domain=[("purchase_ok", "=", True)],
        tracking=True,
    )
    
    # Link to purchase order lines
    purchase_lines = fields.Many2many(
        comodel_name="purchase.order.line",
        relation="h_jubran_pr_purchase_order_line_rel",
        column1="purchase_request_line_id",
        column2="purchase_order_line_id",
        string="Purchase Order Lines",
        readonly=True,
        copy=False,
    )
    
    # Custom fields
    project_id = fields.Many2one(
        'h_jubran.project',
        string='Project',
        related='request_id.project_id',
        store=True,
        readonly=True
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
    master_element_id = fields.Many2one(
        'h_jubran.master.element',
        string='Element',
        domain="[('subcategory_id', '=', subcategory_id)]",
        help="Master data element for cost classification."
    )
    boq_rate = fields.Monetary(
        string='BOQ Rate',
        currency_field='currency_id',
        compute='_compute_boq_rate',
        store=True,
        readonly=True,
        help="Rate from BOQ Summary for this category and subcategory."
    )
    rate = fields.Monetary(
        string='Unit Price',
        currency_field='currency_id',
        help="Unit price for this line item."
    )
    amount = fields.Monetary(
        string='Amount',
        currency_field='currency_id',
        compute='_compute_amount',
        store=True,
        help="Total amount (Quantity * Unit Price)."
    )
    pending_qty_to_receive = fields.Float(
        compute="_compute_pending_qty",
        digits="Product Unit of Measure",
        string="Pending Qty to Receive",
        store=True,
    )

    @api.depends('product_qty', 'rate')
    def _compute_amount(self):
        """Compute amount from quantity and rate."""
        for line in self:
            line.amount = (line.product_qty or 0.0) * (line.rate or 0.0)

    @api.depends('product_qty', 'purchase_lines')
    def _compute_pending_qty(self):
        """Compute pending quantity to receive."""
        for line in self:
            purchased_qty = sum(line.purchase_lines.mapped('product_qty'))
            line.pending_qty_to_receive = max(0.0, line.product_qty - purchased_qty)

    @api.depends('project_id', 'category_id', 'subcategory_id', 'request_id.project_id')
    def _compute_boq_rate(self):
        """Compute BOQ rate from BOQ summary based on project, category, and subcategory."""
        for line in self:
            line.boq_rate = 0.0
            project_id = line.project_id.id if line.project_id else (line.request_id.project_id.id if line.request_id and line.request_id.project_id else False)
            if not project_id or not line.subcategory_id:
                continue
            
            # Find BOQ summary for this project
            boq_summary = self.env['h_jubran.boq.summary'].search([
                ('project_id', '=', project_id)
            ], limit=1)
            
            if not boq_summary:
                continue
            
            # Find BOQ summary line matching category and subcategory
            domain = [
                ('summary_id', '=', boq_summary.id),
                ('subcategory_id', '=', line.subcategory_id.id)
            ]
            if line.category_id:
                domain.append(('category_id', '=', line.category_id.id))
            
            boq_line = self.env['h_jubran.boq.summary.line'].search(domain, limit=1)
            
            if boq_line and boq_line.rate:
                line.boq_rate = boq_line.rate
    
    @api.onchange('subcategory_id')
    def _onchange_subcategory_id(self):
        """Update category when subcategory changes, clear element."""
        if self.subcategory_id:
            self.category_id = self.subcategory_id.category_id.id
        self.master_element_id = False

    @api.onchange('master_element_id')
    def _onchange_master_element_id(self):
        """Update subcategory and category when element changes."""
        if self.master_element_id:
            self.subcategory_id = self.master_element_id.subcategory_id.id
            self.category_id = self.master_element_id.category_id.id

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = f"[{self.product_id.code}] {name}"
            if self.product_id.description_purchase:
                name += "\n" + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = name


    def do_cancel(self):
        """Actions to perform when cancelling a purchase request line."""
        self.write({"cancelled": True})

    def do_uncancel(self):
        """Actions to perform when uncancelling a purchase request line."""
        self.write({"cancelled": False})

