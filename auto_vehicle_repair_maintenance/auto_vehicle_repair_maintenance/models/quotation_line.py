# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class QuotationLine(models.Model):
    _name = 'auto.vehicle.repair.quotation.line'
    _description = 'Inspection Quotation Line'
    _order = 'sequence, id'

    inspection_id = fields.Many2one(
        'auto.vehicle.repair.inspection',
        string='Inspection',
        required=True,
        ondelete='cascade',
        index=True
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of the line'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product/Service',
        domain=[('sale_ok', '=', True)],
        help='Product or service for this repair'
    )
    description = fields.Text(
        string='Description',
        required=True,
        help='Description of the work or part'
    )
    quantity = fields.Float(
        string='Quantity',
        default=1.0,
        required=True,
        digits='Product Unit of Measure',
        help='Quantity of product/service'
    )
    unit_price = fields.Float(
        string='Unit Price',
        required=True,
        digits=(16, 2),
        help='Price per unit'
    )
    subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True,
        digits=(16, 2),
        help='Quantity × Unit Price'
    )
    is_labor = fields.Boolean(
        string='Is Labor?',
        default=False,
        help='Check if this is a labor/service charge'
    )
    labor_hours = fields.Float(
        string='Labor Hours',
        digits=(16, 2),
        help='Number of labor hours (if applicable)'
    )
    qty_available = fields.Float(
        string='Quantity on Hand',
        compute='_compute_qty_available',
        store=False,
        digits='Product Unit of Measure',
        help='Available quantity in stock for this product'
    )
    
    @api.depends('product_id')
    def _compute_qty_available(self):
        """Compute quantity on hand from product stock"""
        for line in self:
            if line.product_id:
                line.qty_available = line.product_id.qty_available
            else:
                line.qty_available = 0.0
    
    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name
            self.unit_price = self.product_id.list_price
            if self.product_id.type == 'service':
                self.is_labor = True
    
    @api.constrains('quantity', 'unit_price')
    def _check_positive_values(self):
        for line in self:
            if line.quantity < 0:
                raise ValidationError(_('Quantity cannot be negative.'))
            if line.unit_price < 0:
                raise ValidationError(_('Unit price cannot be negative.'))

