# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta


class WorkOrder(models.Model):
    _name = 'auto.vehicle.repair.work.order'
    _description = 'Work Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Work Order Reference',
        required=True,
        index=True,
        default=lambda self: _('New'),
        tracking=True,
        help='Auto-generated work order reference number'
    )
    inspection_id = fields.Many2one(
        'auto.vehicle.repair.inspection',
        string='Inspection',
        required=True,
        tracking=True,
        ondelete='restrict',
        readonly=True,
        help='Related inspection'
    )
    vehicle_id = fields.Many2one(
        'auto.vehicle.repair.vehicle',
        string='Vehicle',
        required=True,
        tracking=True,
        ondelete='restrict',
        readonly=True,
        help='Vehicle being repaired'
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        tracking=True,
        readonly=True,
        help='Customer who owns the vehicle'
    )
    
    # Sale Order
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Quotation/Sale Order',
        tracking=True,
        readonly=True,
        help='Related sale order (quotation)'
    )
    quotation_amount = fields.Float(
        string='Quotation Amount',
        related='inspection_id.quotation_amount',
        store=True,
        readonly=True,
        digits=(16, 2),
        help='Total amount from inspection quotation'
    )
    
    # Work Order Fields
    assigned_mechanic_id = fields.Many2one(
        'hr.employee',
        string='Assigned Mechanic/Technician',
        tracking=True,
        domain=[('job_id.name', 'ilike', 'mechanic')],
        help='Mechanic assigned to this job'
    )
    start_date = fields.Datetime(
        string='Work Started',
        default=fields.Datetime.now,
        tracking=True,
        help='When work started'
    )
    work_order_done_date = fields.Datetime(
        string='Work Order Completed',
        tracking=True,
        help='When work order was marked as done'
    )
    end_date = fields.Datetime(
        string='Job Finalized',
        tracking=True,
        help='When repair job was finalized'
    )
    work_description = fields.Text(
        string='Work Description/Notes',
        tracking=True,
        help='Description of work performed'
    )
    
    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', required=True, tracking=True,
        help='Current state of the work order')
    
    # Maintenance - Inherited from Inspection
    is_maintenance = fields.Boolean(
        string='Is Maintenance?',
        tracking=True,
        help='Whether this is a maintenance job'
    )
    periodic_maintenance_interval = fields.Selection([
        ('1', 'Every 1 Month'),
        ('3', 'Every 3 Months'),
        ('6', 'Every 6 Months'),
        ('12', 'Every 12 Months'),
    ], string='Periodic Maintenance Interval',
        help='Interval for periodic maintenance'
    )
    next_maintenance_date = fields.Date(
        string='Next Maintenance Date',
        compute='_compute_next_maintenance_date',
        store=True,
        help='Automatically calculated next maintenance date'
    )
    
    # Related maintenance record
    maintenance_record_id = fields.Many2one(
        'auto.vehicle.repair.maintenance',
        string='Related Maintenance Record',
        readonly=True,
        help='Maintenance record created from this work order'
    )
    
    # Inspection Details (copied from inspection)
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
        readonly=True
    )
    engine_notes = fields.Text(string='Engine Notes', readonly=True)
    engine_oil_level = fields.Selection(
        selection=[
            ('adequate', 'Adequate'),
            ('low', 'Low'),
            ('overfilled', 'Overfilled'),
        ],
        string='Engine Oil Level',
        readonly=True
    )
    engine_coolant_level = fields.Selection(
        selection=[
            ('adequate', 'Adequate'),
            ('low', 'Low'),
            ('empty', 'Empty'),
        ],
        string='Coolant Level',
        readonly=True
    )
    engine_belts_condition = fields.Selection(
        selection=[
            ('good', 'Good'),
            ('worn', 'Worn'),
            ('damaged', 'Damaged'),
        ],
        string='Belts Condition',
        readonly=True
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
        readonly=True
    )
    brakes_notes = fields.Text(string='Brakes Notes', readonly=True)
    brake_pads_thickness = fields.Char(string='Brake Pads Thickness', readonly=True)
    brake_fluid_level = fields.Selection(
        selection=[
            ('adequate', 'Adequate'),
            ('low', 'Low'),
            ('empty', 'Empty'),
        ],
        string='Brake Fluid Level',
        readonly=True
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
        readonly=True
    )
    tires_notes = fields.Text(string='Tires Notes', readonly=True)
    tire_pressure_front = fields.Char(string='Front Tire Pressure', readonly=True)
    tire_pressure_rear = fields.Char(string='Rear Tire Pressure', readonly=True)
    tire_tread_depth = fields.Char(string='Tire Tread Depth', readonly=True)
    
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
        readonly=True
    )
    electrical_notes = fields.Text(string='Electrical Notes', readonly=True)
    battery_voltage = fields.Char(string='Battery Voltage', readonly=True)
    battery_condition = fields.Selection(
        selection=[
            ('good', 'Good'),
            ('weak', 'Weak'),
            ('dead', 'Dead'),
        ],
        string='Battery Condition',
        readonly=True
    )
    lights_condition = fields.Selection(
        selection=[
            ('all_working', 'All Working'),
            ('some_not_working', 'Some Not Working'),
            ('many_not_working', 'Many Not Working'),
        ],
        string='Lights Condition',
        readonly=True
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
        readonly=True
    )
    body_notes = fields.Text(string='Body Notes', readonly=True)
    paint_condition = fields.Selection(
        selection=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
        ],
        string='Paint Condition',
        readonly=True
    )
    windshield_condition = fields.Selection(
        selection=[
            ('good', 'Good'),
            ('cracked', 'Cracked'),
            ('damaged', 'Damaged'),
        ],
        string='Windshield Condition',
        readonly=True
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
        readonly=True
    )
    suspension_notes = fields.Text(string='Suspension Notes', readonly=True)
    steering_condition = fields.Selection(
        selection=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
        ],
        string='Steering Condition',
        readonly=True
    )
    
    # Air Conditioning
    ac_condition = fields.Selection(
        selection=[
            ('working', 'Working'),
            ('not_working', 'Not Working'),
            ('needs_service', 'Needs Service'),
        ],
        string='AC Condition',
        readonly=True
    )
    ac_notes = fields.Text(string='AC Notes', readonly=True)
    
    # General Inspection
    inspection_notes = fields.Text(
        string='General Inspection Notes',
        readonly=True
    )
    inspection_mileage = fields.Integer(
        string='Inspection Mileage',
        readonly=True
    )
    overall_condition = fields.Selection(
        selection=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
            ('critical', 'Critical'),
        ],
        string='Overall Condition',
        readonly=True
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
                vals['name'] = self.env['ir.sequence'].next_by_code('auto.vehicle.repair.work.order') or _('New')
        return super().create(vals_list)
    
    @api.depends('is_maintenance', 'periodic_maintenance_interval', 'end_date', 'state')
    def _compute_next_maintenance_date(self):
        for work_order in self:
            if work_order.is_maintenance and work_order.periodic_maintenance_interval and work_order.state == 'done' and work_order.end_date:
                if isinstance(work_order.end_date, str):
                    end_date = fields.Datetime.from_string(work_order.end_date).date()
                else:
                    end_date = work_order.end_date.date() if hasattr(work_order.end_date, 'date') else work_order.end_date
                interval_months = int(work_order.periodic_maintenance_interval)
                days_to_add = interval_months * 30
                work_order.next_maintenance_date = end_date + timedelta(days=days_to_add)
            else:
                work_order.next_maintenance_date = False
    
    @api.depends('engine_condition', 'brakes_condition', 'tires_condition', 'electrical_condition', 'body_condition', 'overall_condition')
    def _compute_selection_labels(self):
        """Compute human-readable labels for selection fields"""
        for work_order in self:
            engine_selection = [('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'), ('critical', 'Critical')]
            work_order.engine_condition_label = dict(engine_selection).get(work_order.engine_condition, 'N/A')
            
            brakes_selection = [('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'), ('critical', 'Critical')]
            work_order.brakes_condition_label = dict(brakes_selection).get(work_order.brakes_condition, 'N/A')
            
            tires_selection = [('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'), ('critical', 'Critical')]
            work_order.tires_condition_label = dict(tires_selection).get(work_order.tires_condition, 'N/A')
            
            electrical_selection = [('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'), ('critical', 'Critical')]
            work_order.electrical_condition_label = dict(electrical_selection).get(work_order.electrical_condition, 'N/A')
            
            body_selection = [('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor')]
            work_order.body_condition_label = dict(body_selection).get(work_order.body_condition, 'N/A')
            
            overall_selection = [('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'), ('critical', 'Critical')]
            work_order.overall_condition_label = dict(overall_selection).get(work_order.overall_condition, 'N/A')
    
    def action_start_work(self):
        """Start work order"""
        for work_order in self:
            if work_order.state != 'draft':
                raise UserError(_('Work order must be in Draft state to start.'))
            work_order.write({
                'state': 'in_progress',
                'start_date': fields.Datetime.now()
            })
        return True
    
    def action_work_order_done(self):
        """Mark work order as done"""
        for work_order in self:
            if work_order.state != 'in_progress':
                raise UserError(_('Work order must be in Progress state to mark as done.'))
            work_order.write({
                'state': 'done',
                'work_order_done_date': fields.Datetime.now()
            })
        return True
    
    def action_finalize(self):
        """Finalize work order and trigger maintenance schedule if applicable"""
        for work_order in self:
            if work_order.state != 'done':
                raise UserError(_('Work order must be in Done state to finalize.'))
            
            work_order.write({
                'end_date': fields.Datetime.now()
            })
            
            # Create maintenance record if this is a maintenance job
            if work_order.is_maintenance and work_order.periodic_maintenance_interval:
                work_order._create_maintenance_record()
        return True
    
    def _create_maintenance_record(self):
        """Create maintenance record when work order is finalized"""
        self.ensure_one()
        if not self.next_maintenance_date:
            return
        
        maintenance = self.env['auto.vehicle.repair.maintenance'].create({
            'vehicle_id': self.vehicle_id.id,
            'customer_id': self.customer_id.id,
            'related_work_order_id': self.id,
            'scheduled_maintenance_date': self.next_maintenance_date,
            'status': 'pending',
        })
        
        self.write({'maintenance_record_id': maintenance.id})
        return maintenance
    
    def action_cancel(self):
        """Cancel work order"""
        for work_order in self:
            if work_order.state in ('done',):
                raise UserError(_('Cannot cancel a work order that is already done.'))
            work_order.write({'state': 'cancelled'})
        return True
    
    def action_view_inspection(self):
        """Open the related inspection"""
        self.ensure_one()
        return {
            'name': _('Inspection'),
            'type': 'ir.actions.act_window',
            'res_model': 'auto.vehicle.repair.inspection',
            'res_id': self.inspection_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

