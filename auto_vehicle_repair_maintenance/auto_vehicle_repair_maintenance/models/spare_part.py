# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class SparePart(models.Model):
    _name = 'auto.vehicle.repair.spare.part'
    _description = 'Spare Part'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Spare Part Name',
        required=True,
        index=True,
        tracking=True,
        help='Name of the spare part'
    )
    code = fields.Char(
        string='Part Code/Reference',
        index=True,
        tracking=True,
        help='Part number or reference code'
    )
    vehicle_id = fields.Many2one(
        'auto.vehicle.repair.vehicle',
        string='Vehicle',
        tracking=True,
        help='Vehicle this spare part is for (optional - can be generic)'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        tracking=True,
        domain=[('type', '=', 'product')],
        help='Select product from inventory for this spare part'
    )
    quantity = fields.Float(
        string='Quantity',
        default=0.0,
        required=True,
        tracking=True,
        digits='Product Unit of Measure',
        help='Current quantity of this spare part'
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Storage Location',
        domain=[('usage', '=', 'internal')],
        tracking=True,
        help='Warehouse location where this spare part is stored'
    )
    min_quantity = fields.Float(
        string='Minimum Quantity',
        default=0.0,
        digits='Product Unit of Measure',
        help='Minimum quantity to maintain in stock'
    )
    max_quantity = fields.Float(
        string='Maximum Quantity',
        default=0.0,
        digits='Product Unit of Measure',
        help='Maximum quantity to store'
    )
    unit_price = fields.Float(
        string='Unit Price',
        digits=(16, 2),
        help='Cost per unit'
    )
    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True, tracking=True)
    
    # Computed fields
    available_quantity = fields.Float(
        string='Available in Stock',
        compute='_compute_available_quantity',
        store=False,
        help='Actual quantity available in inventory'
    )
    
    @api.depends('product_id', 'location_id')
    def _compute_available_quantity(self):
        """Compute available quantity from stock"""
        for part in self:
            if part.product_id and part.location_id:
                quants = self.env['stock.quant'].search([
                    ('product_id', '=', part.product_id.id),
                    ('location_id', '=', part.location_id.id),
                ])
                part.available_quantity = sum(quants.mapped('quantity'))
            else:
                part.available_quantity = 0.0
    
    @api.model_create_multi
    def create(self, vals_list):
        """Create spare part"""
        parts = super().create(vals_list)
        return parts
    
    def write(self, vals):
        """Update spare part"""
        return super().write(vals)
    
    @api.constrains('quantity', 'min_quantity', 'max_quantity')
    def _check_quantities(self):
        for part in self:
            if part.min_quantity < 0:
                raise ValidationError(_('Minimum quantity cannot be negative.'))
            if part.max_quantity < 0:
                raise ValidationError(_('Maximum quantity cannot be negative.'))
            if part.max_quantity > 0 and part.min_quantity > part.max_quantity:
                raise ValidationError(_('Minimum quantity cannot be greater than maximum quantity.'))
    
    def action_sync_with_inventory(self):
        """Sync quantity with actual inventory"""
        for part in self:
            if part.product_id and part.location_id:
                part.quantity = part.available_quantity
        return True

