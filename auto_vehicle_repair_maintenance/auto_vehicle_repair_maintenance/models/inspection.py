# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class Inspection(models.Model):
    _name = 'auto.vehicle.repair.inspection'
    _description = 'Vehicle Inspection'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Inspection Reference',
        required=True,
        index=True,
        default=lambda self: _('New'),
        tracking=True,
        help='Auto-generated inspection reference number'
    )
    vehicle_id = fields.Many2one(
        'auto.vehicle.repair.vehicle',
        string='Vehicle',
        required=True,
        tracking=True,
        ondelete='restrict',
        help='Vehicle being inspected'
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=False,
        tracking=True,
        help='Customer who owns the vehicle'
    )
    
    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        """Auto-fill customer from vehicle owner"""
        if self.vehicle_id and self.vehicle_id.owner_id:
            self.customer_id = self.vehicle_id.owner_id
    
    # Inspection - Comprehensive Fields
    inspection_date = fields.Datetime(
        string='Inspection Date',
        default=fields.Datetime.now,
        tracking=True,
        help='Date and time of inspection'
    )
    inspected_by_id = fields.Many2one(
        'hr.employee',
        string='Inspected By',
        tracking=True,
        help='Employee who performed the inspection'
    )
    
    # Engine Inspection
    engine_condition = fields.Selection(
        selection=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
            ('critical', 'Critical'),
        ],
        string='Engine Condition',
        tracking=True
    )
    engine_notes = fields.Text(string='Engine Notes')
    engine_oil_level = fields.Selection(
        selection=[
            ('adequate', 'Adequate'),
            ('low', 'Low'),
            ('overfilled', 'Overfilled'),
        ],
        string='Engine Oil Level'
    )
    engine_coolant_level = fields.Selection(
        selection=[
            ('adequate', 'Adequate'),
            ('low', 'Low'),
            ('empty', 'Empty'),
        ],
        string='Coolant Level'
    )
    engine_belts_condition = fields.Selection(
        selection=[
            ('good', 'Good'),
            ('worn', 'Worn'),
            ('damaged', 'Damaged'),
        ],
        string='Belts Condition'
    )
    
    # Brakes Inspection
    brakes_condition = fields.Selection(
        selection=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
            ('critical', 'Critical'),
        ],
        string='Brakes Condition',
        tracking=True
    )
    brakes_notes = fields.Text(string='Brakes Notes')
    brake_pads_thickness = fields.Char(string='Brake Pads Thickness')
    brake_fluid_level = fields.Selection(
        selection=[
            ('adequate', 'Adequate'),
            ('low', 'Low'),
            ('empty', 'Empty'),
        ],
        string='Brake Fluid Level'
    )
    
    # Tires Inspection
    tires_condition = fields.Selection(
        selection=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
            ('critical', 'Critical'),
        ],
        string='Tires Condition',
        tracking=True
    )
    tires_notes = fields.Text(string='Tires Notes')
    tire_pressure_front = fields.Char(string='Front Tire Pressure')
    tire_pressure_rear = fields.Char(string='Rear Tire Pressure')
    tire_tread_depth = fields.Char(string='Tire Tread Depth')
    
    # Electrical System
    electrical_condition = fields.Selection(
        selection=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
            ('critical', 'Critical'),
        ],
        string='Electrical Condition',
        tracking=True
    )
    electrical_notes = fields.Text(string='Electrical Notes')
    battery_voltage = fields.Char(string='Battery Voltage')
    battery_condition = fields.Selection(
        selection=[
            ('good', 'Good'),
            ('weak', 'Weak'),
            ('dead', 'Dead'),
        ],
        string='Battery Condition'
    )
    lights_condition = fields.Selection(
        selection=[
            ('all_working', 'All Working'),
            ('some_not_working', 'Some Not Working'),
            ('many_not_working', 'Many Not Working'),
        ],
        string='Lights Condition'
    )
    
    # Body & Exterior
    body_condition = fields.Selection(
        selection=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
        ],
        string='Body Condition',
        tracking=True
    )
    body_notes = fields.Text(string='Body Notes')
    paint_condition = fields.Selection(
        selection=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
        ],
        string='Paint Condition'
    )
    windshield_condition = fields.Selection(
        selection=[
            ('good', 'Good'),
            ('cracked', 'Cracked'),
            ('damaged', 'Damaged'),
        ],
        string='Windshield Condition'
    )
    
    # Suspension & Steering
    suspension_condition = fields.Selection(
        selection=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
        ],
        string='Suspension Condition',
        tracking=True
    )
    suspension_notes = fields.Text(string='Suspension Notes')
    steering_condition = fields.Selection(
        selection=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
        ],
        string='Steering Condition'
    )
    
    # Air Conditioning
    ac_condition = fields.Selection(
        selection=[
            ('working', 'Working'),
            ('not_working', 'Not Working'),
            ('needs_service', 'Needs Service'),
        ],
        string='AC Condition',
        tracking=True
    )
    ac_notes = fields.Text(string='AC Notes')
    
    # General Inspection
    inspection_notes = fields.Text(
        string='General Inspection Notes',
        tracking=True,
        help='General findings and notes from vehicle inspection'
    )
    inspection_mileage = fields.Integer(
        string='Inspection Mileage',
        tracking=True,
        help='Vehicle mileage at time of inspection'
    )
    inspection_images = fields.Many2many(
        'ir.attachment',
        string='Inspection Images',
        help='Attach inspection photos'
    )
    
    # Overall Assessment
    overall_condition = fields.Selection(
        selection=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
            ('critical', 'Critical'),
        ],
        string='Overall Condition',
        tracking=True,
        help='Overall vehicle condition assessment'
    )
    estimated_repair_cost = fields.Float(
        string='Estimated Repair Cost',
        digits=(16, 2),
        help='Initial estimated cost before detailed quotation'
    )
    
    # Quotation - Sale Order Integration
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Quotation/Sale Order',
        tracking=True,
        readonly=True,
        help='Related sale order (quotation)'
    )
    quotation_amount = fields.Float(
        string='Quotation Amount',
        compute='_compute_quotation_amount',
        store=True,
        tracking=True,
        digits=(16, 2),
        help='Total amount from sale order'
    )
    quotation_line_ids = fields.One2many(
        'auto.vehicle.repair.quotation.line',
        'inspection_id',
        string='Quotation Lines',
        help='Products and services for this repair job'
    )
    
    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Inspection Completed'),
        ('quotation', 'Quotation Created'),
        ('accepted', 'Quotation Accepted'),
        ('work_order_created', 'Work Order Created'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', required=True, tracking=True,
        help='Current state of the inspection')
    
    # Related work order
    work_order_id = fields.Many2one(
        'auto.vehicle.repair.work.order',
        string='Work Order',
        readonly=True,
        help='Work order created from this inspection'
    )
    
    # Maintenance - Inherited from Vehicle
    is_maintenance = fields.Boolean(
        string='Is Maintenance?',
        compute='_compute_is_maintenance',
        store=True,
        tracking=True,
        help='Automatically set based on vehicle maintenance settings'
    )
    periodic_maintenance_interval = fields.Selection([
        ('1', 'Every 1 Month'),
        ('3', 'Every 3 Months'),
        ('6', 'Every 6 Months'),
        ('12', 'Every 12 Months'),
    ], string='Periodic Maintenance Interval',
        compute='_compute_maintenance_interval',
        store=True,
        help='Interval for periodic maintenance (inherited from vehicle)'
    )
    
    # Computed fields for reports
    engine_condition_label = fields.Char(compute='_compute_selection_labels', store=False)
    brakes_condition_label = fields.Char(compute='_compute_selection_labels', store=False)
    tires_condition_label = fields.Char(compute='_compute_selection_labels', store=False)
    electrical_condition_label = fields.Char(compute='_compute_selection_labels', store=False)
    body_condition_label = fields.Char(compute='_compute_selection_labels', store=False)
    overall_condition_label = fields.Char(compute='_compute_selection_labels', store=False)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('auto.vehicle.repair.inspection') or _('New')
        return super().create(vals_list)
    
    @api.depends('sale_order_id', 'sale_order_id.amount_total')
    def _compute_quotation_amount(self):
        for inspection in self:
            if inspection.sale_order_id:
                inspection.quotation_amount = inspection.sale_order_id.amount_total
            elif inspection.quotation_line_ids:
                inspection.quotation_amount = sum(line.subtotal for line in inspection.quotation_line_ids)
            else:
                inspection.quotation_amount = 0.0
    
    @api.depends('vehicle_id', 'vehicle_id.is_maintenance_enabled')
    def _compute_is_maintenance(self):
        for inspection in self:
            inspection.is_maintenance = inspection.vehicle_id.is_maintenance_enabled if inspection.vehicle_id else False
    
    @api.depends('vehicle_id', 'vehicle_id.periodic_maintenance_interval')
    def _compute_maintenance_interval(self):
        for inspection in self:
            inspection.periodic_maintenance_interval = inspection.vehicle_id.periodic_maintenance_interval if inspection.vehicle_id else False
    
    @api.depends('engine_condition', 'brakes_condition', 'tires_condition', 'electrical_condition', 'body_condition', 'overall_condition')
    def _compute_selection_labels(self):
        """Compute human-readable labels for selection fields"""
        for inspection in self:
            # Engine condition
            engine_selection = [('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'), ('critical', 'Critical')]
            inspection.engine_condition_label = dict(engine_selection).get(inspection.engine_condition, 'N/A')
            
            # Brakes condition
            brakes_selection = [('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'), ('critical', 'Critical')]
            inspection.brakes_condition_label = dict(brakes_selection).get(inspection.brakes_condition, 'N/A')
            
            # Tires condition
            tires_selection = [('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'), ('critical', 'Critical')]
            inspection.tires_condition_label = dict(tires_selection).get(inspection.tires_condition, 'N/A')
            
            # Electrical condition
            electrical_selection = [('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'), ('critical', 'Critical')]
            inspection.electrical_condition_label = dict(electrical_selection).get(inspection.electrical_condition, 'N/A')
            
            # Body condition
            body_selection = [('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor')]
            inspection.body_condition_label = dict(body_selection).get(inspection.body_condition, 'N/A')
            
            # Overall condition
            overall_selection = [('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'), ('critical', 'Critical')]
            inspection.overall_condition_label = dict(overall_selection).get(inspection.overall_condition, 'N/A')
    
    def action_complete_inspection(self):
        """Mark inspection as completed"""
        for inspection in self:
            if inspection.state != 'draft':
                raise UserError(_('Inspection must be in Draft state to complete.'))
            inspection.write({'state': 'completed'})
        return True
    
    def action_create_quotation(self):
        """Create quotation from inspection"""
        for inspection in self:
            if inspection.state not in ('draft', 'completed'):
                raise UserError(_('Inspection must be completed before creating quotation.'))
            
            if not inspection.customer_id:
                raise UserError(_('Please set a customer before creating quotation.'))
            
            # Create sale order if not exists
            if not inspection.sale_order_id:
                sale_order = inspection._create_sale_order()
                inspection.write({
                    'state': 'quotation',
                    'sale_order_id': sale_order.id
                })
            else:
                inspection.write({'state': 'quotation'})
        return True
    
    def _create_sale_order(self):
        """Create sale order (quotation) from inspection"""
        self.ensure_one()
        
        if not self.customer_id:
            raise UserError(_('Customer is required to create a quotation.'))
        
        sale_order_vals = {
            'partner_id': self.customer_id.id,
            'client_order_ref': f'Inspection: {self.name}',
            'date_order': fields.Datetime.now(),
        }
        
        SaleOrder = self.env['sale.order'].sudo()
        sale_order = SaleOrder.with_context({}).create(sale_order_vals)
        sale_order.write({'inspection_id': self.id})
        
        # Add quotation lines to sale order
        for line in self.quotation_line_ids:
            self.env['sale.order.line'].create({
                'order_id': sale_order.id,
                'product_id': line.product_id.id if line.product_id else False,
                'name': line.description or (line.product_id.name if line.product_id else 'Repair Service'),
                'product_uom_qty': line.quantity,
                'price_unit': line.unit_price,
            })
        
        return self.env['sale.order'].browse(sale_order.id)
    
    def action_accept_quotation(self):
        """Accept quotation and create work order"""
        for inspection in self:
            if inspection.state != 'quotation':
                raise UserError(_('Inspection must be in Quotation state to accept.'))
            
            # Confirm sale order if exists
            if inspection.sale_order_id and inspection.sale_order_id.state == 'draft':
                inspection.sale_order_id.action_confirm()
            
            # Create work order
            work_order = inspection._create_work_order()
            
            inspection.write({
                'state': 'work_order_created',
                'work_order_id': work_order.id
            })
        return True
    
    def _create_work_order(self):
        """Create work order from inspection"""
        self.ensure_one()
        
        work_order_vals = {
            'name': self.env['ir.sequence'].next_by_code('auto.vehicle.repair.work.order') or _('New'),
            'inspection_id': self.id,
            'vehicle_id': self.vehicle_id.id,
            'customer_id': self.customer_id.id,
            'sale_order_id': self.sale_order_id.id if self.sale_order_id else False,
            'is_maintenance': self.is_maintenance,
            'periodic_maintenance_interval': self.periodic_maintenance_interval,
        }
        
        work_order = self.env['auto.vehicle.repair.work.order'].create(work_order_vals)
        
        # Copy inspection details to work order
        inspection_fields = [
            'engine_condition', 'engine_notes', 'engine_oil_level', 'engine_coolant_level', 'engine_belts_condition',
            'brakes_condition', 'brakes_notes', 'brake_pads_thickness', 'brake_fluid_level',
            'tires_condition', 'tires_notes', 'tire_pressure_front', 'tire_pressure_rear', 'tire_tread_depth',
            'electrical_condition', 'electrical_notes', 'battery_voltage', 'battery_condition', 'lights_condition',
            'body_condition', 'body_notes', 'paint_condition', 'windshield_condition',
            'suspension_condition', 'suspension_notes', 'steering_condition',
            'ac_condition', 'ac_notes',
            'inspection_notes', 'inspection_mileage', 'overall_condition',
        ]
        
        copy_vals = {}
        for field in inspection_fields:
            if hasattr(self, field):
                copy_vals[field] = self[field]
        
        work_order.write(copy_vals)
        
        return work_order
    
    def action_view_quotation(self):
        """Open the related sale order"""
        self.ensure_one()
        if not self.sale_order_id:
            raise UserError(_('No quotation has been created yet.'))
        
        return {
            'name': _('Quotation'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_view_work_order(self):
        """Open the related work order"""
        self.ensure_one()
        if not self.work_order_id:
            raise UserError(_('No work order has been created yet.'))
        
        return {
            'name': _('Work Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'auto.vehicle.repair.work.order',
            'res_id': self.work_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_cancel(self):
        """Cancel inspection"""
        for inspection in self:
            if inspection.state in ('work_order_created', 'accepted'):
                raise UserError(_('Cannot cancel an inspection that has a work order.'))
            inspection.write({'state': 'cancelled'})
        return True
    
    @api.constrains('quotation_amount')
    def _check_quotation_amount(self):
        for inspection in self:
            if inspection.quotation_amount and inspection.quotation_amount < 0:
                raise ValidationError(_('Quotation amount cannot be negative.'))

