# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    inspection_id = fields.Many2one(
        'auto.vehicle.repair.inspection',
        string='Inspection',
        ondelete='set null',
        tracking=True,
        help='Related inspection'
    )
    vehicle_id = fields.Many2one(
        'auto.vehicle.repair.vehicle',
        string='Vehicle',
        related='inspection_id.vehicle_id',
        store=True,
        readonly=True,
        help='Vehicle from inspection'
    )

