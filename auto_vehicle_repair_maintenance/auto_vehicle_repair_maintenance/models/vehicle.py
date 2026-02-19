# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Vehicle(models.Model):
    _name = 'auto.vehicle.repair.vehicle'
    _description = 'Vehicle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Vehicle Name/Model',
        required=True,
        index=True,
        tracking=True,
        help='Vehicle identification name or model (auto-filled from product)'
    )
    license_plate = fields.Char(
        string='License Plate',
        tracking=True,
        help='Vehicle license plate number'
    )
    vin = fields.Char(
        string='VIN',
        tracking=True,
        help='Vehicle Identification Number'
    )
    make = fields.Char(
        string='Make/Brand',
        tracking=True,
        help='Vehicle manufacturer or brand'
    )
    year = fields.Integer(
        string='Year of Manufacture',
        tracking=True,
        help='Year the vehicle was manufactured'
    )
    owner_id = fields.Many2one(
        'res.partner',
        string='Owner (Customer)',
        required=True,
        tracking=True,
        help='Owner of the vehicle'
    )
    
    # Relations
    inspection_ids = fields.One2many(
        'auto.vehicle.repair.inspection',
        'vehicle_id',
        string='Inspections',
        help='All inspections for this vehicle'
    )
    work_order_ids = fields.One2many(
        'auto.vehicle.repair.work.order',
        'vehicle_id',
        string='Work Orders',
        help='All work orders for this vehicle'
    )
    maintenance_record_ids = fields.One2many(
        'auto.vehicle.repair.maintenance',
        'vehicle_id',
        string='Maintenance History',
        help='Maintenance records for this vehicle'
    )
    spare_part_ids = fields.One2many(
        'auto.vehicle.repair.spare.part',
        'vehicle_id',
        string='Spare Parts',
        help='Spare parts for this vehicle'
    )
    
    # Inventory Integration
    product_id = fields.Many2one(
        'product.product',
        string='Product in Inventory',
        required=True,
        tracking=True,
        domain=[('type', '=', 'product')],
        help='Select product from inventory for this vehicle'
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Storage Location',
        domain=[('usage', '=', 'internal')],
        tracking=True,
        help='Warehouse location where vehicle is stored'
    )
    
    # Computed fields
    inspection_count = fields.Integer(
        string='Inspections',
        compute='_compute_inspection_count',
        store=False
    )
    work_order_count = fields.Integer(
        string='Work Orders',
        compute='_compute_work_order_count',
        store=False
    )
    maintenance_count = fields.Integer(
        string='Maintenance Records',
        compute='_compute_maintenance_count',
        store=False
    )
    active_work_orders = fields.Integer(
        string='Active Work Orders',
        compute='_compute_active_work_orders',
        store=False
    )
    
    # Maintenance Settings
    is_maintenance_enabled = fields.Boolean(
        string='Maintenance Enabled',
        default=False,
        tracking=True,
        help='If enabled, this vehicle will always have maintenance jobs and follow maintenance process'
    )
    periodic_maintenance_interval = fields.Selection([
        ('1', 'Every 1 Month'),
        ('3', 'Every 3 Months'),
        ('6', 'Every 6 Months'),
        ('12', 'Every 12 Months'),
    ], string='Periodic Maintenance Interval',
        help='Default maintenance interval for this vehicle (only if Maintenance Enabled is checked)'
    )
    
    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True, tracking=True)
    
    
    @api.depends('inspection_ids')
    def _compute_inspection_count(self):
        for vehicle in self:
            vehicle.inspection_count = len(vehicle.inspection_ids)
    
    @api.depends('work_order_ids')
    def _compute_work_order_count(self):
        for vehicle in self:
            vehicle.work_order_count = len(vehicle.work_order_ids)
    
    @api.depends('maintenance_record_ids')
    def _compute_maintenance_count(self):
        for vehicle in self:
            vehicle.maintenance_count = len(vehicle.maintenance_record_ids)
    
    @api.depends('work_order_ids', 'work_order_ids.state')
    def _compute_active_work_orders(self):
        for vehicle in self:
            active_states = ['draft', 'in_progress']
            vehicle.active_work_orders = len(
                vehicle.work_order_ids.filtered(lambda w: w.state in active_states)
            )
    
    def action_view_inspections(self):
        """Open inspections for this vehicle"""
        self.ensure_one()
        return {
            'name': _('Inspections'),
            'type': 'ir.actions.act_window',
            'res_model': 'auto.vehicle.repair.inspection',
            'view_mode': 'list,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id},
        }
    
    def action_view_work_orders(self):
        """Open work orders for this vehicle"""
        self.ensure_one()
        return {
            'name': _('Work Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'auto.vehicle.repair.work.order',
            'view_mode': 'list,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id},
        }
    
    def action_view_maintenance(self):
        """Open maintenance records for this vehicle"""
        self.ensure_one()
        return {
            'name': _('Maintenance Records'),
            'type': 'ir.actions.act_window',
            'res_model': 'auto.vehicle.repair.maintenance',
            'view_mode': 'list,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id},
        }
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Auto-populate vehicle name from product name"""
        if self.product_id and not self.name:
            self.name = self.product_id.name
    
    @api.constrains('year')
    def _check_year(self):
        current_year = fields.Date.today().year
        for vehicle in self:
            if vehicle.year and (vehicle.year < 1900 or vehicle.year > current_year + 1):
                raise ValidationError(_('Please enter a valid year between 1900 and %s.') % (current_year + 1))

