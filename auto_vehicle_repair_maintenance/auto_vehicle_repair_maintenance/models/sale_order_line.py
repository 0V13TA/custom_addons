# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
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

