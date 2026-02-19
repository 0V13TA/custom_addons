# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class RepairJob(models.Model):
    _name = 'auto.vehicle.repair.job'
    _description = 'Repair Job'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Job Reference',
        required=True,
        index=True,
        default=lambda self: _('New'),
        tracking=True,
        help='Auto-generated job reference number'
    )
    vehicle_id = fields.Many2one(
        'auto.vehicle.repair.vehicle',
        string='Vehicle',
        required=True,
        tracking=True,
        ondelete='restrict',
        help='Vehicle being repaired'
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
        'repair_job_id',
        string='Quotation Lines',
        help='Products and services for this repair job'
    )
    
    @api.depends('sale_order_id', 'sale_order_id.amount_total')
    def _compute_quotation_amount(self):
        for job in self:
            if job.sale_order_id:
                job.quotation_amount = job.sale_order_id.amount_total
            elif job.quotation_line_ids:
                job.quotation_amount = sum(line.subtotal for line in job.quotation_line_ids)
            else:
                job.quotation_amount = 0.0
    
    # Approval
    approval_status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Approval Status', default='pending', tracking=True)
    
    # Work Order
    assigned_mechanic_id = fields.Many2one(
        'hr.employee',
        string='Assigned Mechanic/Technician',
        tracking=True,
        domain=[('job_id.name', 'ilike', 'mechanic')],
        help='Mechanic assigned to this job'
    )
    start_date = fields.Datetime(
        string='Work Started',
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
    next_maintenance_date = fields.Date(
        string='Next Maintenance Date',
        compute='_compute_next_maintenance_date',
        store=True,
        help='Automatically calculated next maintenance date'
    )
    
    @api.depends('vehicle_id', 'vehicle_id.is_maintenance_enabled')
    def _compute_is_maintenance(self):
        for job in self:
            job.is_maintenance = job.vehicle_id.is_maintenance_enabled if job.vehicle_id else False
    
    @api.depends('vehicle_id', 'vehicle_id.periodic_maintenance_interval')
    def _compute_maintenance_interval(self):
        for job in self:
            job.periodic_maintenance_interval = job.vehicle_id.periodic_maintenance_interval if job.vehicle_id else False
    
    # State
    state = fields.Selection([
        ('inspection', 'Inspection'),
        ('quotation', 'Quotation'),
        ('work_order', 'Work Order'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='inspection', required=True, tracking=True,
        help='Current state of the repair job')
    
    # Related maintenance record
    maintenance_record_id = fields.Many2one(
        'auto.vehicle.repair.maintenance',
        string='Related Maintenance Record',
        readonly=True,
        help='Maintenance record created from this job'
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('auto.vehicle.repair.job') or _('New')
        return super().create(vals_list)
    
    @api.depends('is_maintenance', 'periodic_maintenance_interval', 'end_date', 'state')
    def _compute_next_maintenance_date(self):
        for job in self:
            if job.is_maintenance and job.periodic_maintenance_interval and job.state == 'done' and job.end_date:
                # Convert datetime to date
                if isinstance(job.end_date, str):
                    end_date = fields.Datetime.from_string(job.end_date).date()
                else:
                    end_date = job.end_date.date() if hasattr(job.end_date, 'date') else job.end_date
                interval_months = int(job.periodic_maintenance_interval)
                # Calculate days based on months (approximate: 1 month = 30 days)
                days_to_add = interval_months * 30
                job.next_maintenance_date = end_date + timedelta(days=days_to_add)
            else:
                job.next_maintenance_date = False
    
    def action_to_quotation(self):
        """Move from inspection to quotation and create sale order"""
        for job in self:
            if job.state != 'inspection':
                raise UserError(_('Job must be in Inspection state to move to Quotation.'))
            
            if not job.customer_id:
                raise UserError(_('Please set a customer before creating quotation.'))
            
            # Create sale order if not exists
            if not job.sale_order_id:
                sale_order = job._create_sale_order()
                job.write({
                    'state': 'quotation',
                    'sale_order_id': sale_order.id
                })
            else:
                job.write({'state': 'quotation'})
        return True
    
    def _create_sale_order(self):
        """Create sale order (quotation) from repair job"""
        self.ensure_one()
        
        if not self.customer_id:
            raise UserError(_('Customer is required to create a quotation.'))
        
        # Create sale order with minimal required fields only
        # Do NOT set state - it's a readonly computed field in sale.order
        # Create in a completely clean environment to avoid any context issues
        sale_order_vals = {
            'partner_id': self.customer_id.id,
            'client_order_ref': f'Repair Job: {self.name}',
            'date_order': fields.Datetime.now(),
        }
        
        # Create the sale order with empty context to avoid any default conflicts
        # Use sudo to ensure clean environment, then switch back to regular user
        SaleOrder = self.env['sale.order'].sudo()
        sale_order = SaleOrder.with_context({}).create(sale_order_vals)
        
        # Set repair_job_id after creation to avoid any field conflicts
        sale_order.write({'repair_job_id': self.id})
        
        # Add quotation lines to sale order
        for line in self.quotation_line_ids:
            self.env['sale.order.line'].create({
                'order_id': sale_order.id,
                'product_id': line.product_id.id if line.product_id else False,
                'name': line.description or (line.product_id.name if line.product_id else 'Repair Service'),
                'product_uom_qty': line.quantity,
                'price_unit': line.unit_price,
            })
        
        # Return the sale order in the original user's environment
        return self.env['sale.order'].browse(sale_order.id)
    
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
        """View work order - opens form view"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'auto.vehicle.repair.job',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_request_approval(self):
        """Request approval - move to waiting approval state"""
        for job in self:
            if job.state != 'quotation':
                raise UserError(_('Job must be in Quotation state to request approval.'))
            
            # Ensure sale order exists
            if not job.sale_order_id:
                job._create_sale_order()
            
            # Update sale order with quotation lines
            if job.quotation_line_ids and job.sale_order_id:
                # Clear existing lines
                job.sale_order_id.order_line.unlink()
                # Add new lines
                for line in job.quotation_line_ids:
                    self.env['sale.order.line'].create({
                        'order_id': job.sale_order_id.id,
                        'product_id': line.product_id.id if line.product_id else False,
                        'name': line.description or (line.product_id.name if line.product_id else 'Repair Service'),
                        'product_uom_qty': line.quantity,
                        'price_unit': line.unit_price,
                    })
            
            if not job.quotation_amount and not job.quotation_line_ids:
                raise UserError(_('Please add quotation lines or enter a quotation amount before requesting approval.'))
            
            job.write({
                'state': 'waiting_approval',
                'approval_status': 'pending'
            })
        return True
    
    def action_approve(self):
        """Approve job and convert to work order"""
        for job in self:
            if job.state != 'waiting_approval':
                raise UserError(_('Job must be in Waiting Approval state to approve.'))
            
            # Confirm sale order if exists
            if job.sale_order_id and job.sale_order_id.state == 'draft':
                job.sale_order_id.action_confirm()
            
            job.write({
                'state': 'work_order',
                'approval_status': 'approved',
                'start_date': fields.Datetime.now()
            })
        return True
    
    def action_quotation_accepted(self):
        """Accept quotation and move to work order - simplified workflow"""
        for job in self:
            if job.state != 'quotation':
                raise UserError(_('Job must be in Quotation state to accept.'))
            
            # Confirm sale order if exists
            if job.sale_order_id and job.sale_order_id.state == 'draft':
                job.sale_order_id.action_confirm()
            
            job.write({
                'state': 'work_order',
                'approval_status': 'approved',
                'start_date': fields.Datetime.now()
            })
        return True
    
    def action_reject(self):
        """Reject job"""
        for job in self:
            if job.state != 'waiting_approval':
                raise UserError(_('Job must be in Waiting Approval state to reject.'))
            job.write({
                'state': 'cancelled',
                'approval_status': 'rejected'
            })
        return True
    
    def action_work_order_done(self):
        """Mark work order as done"""
        for job in self:
            if job.state != 'work_order':
                raise UserError(_('Job must be in Work Order state to mark work order as done.'))
            
            if not job.work_order_done_date:
                job.write({
                    'work_order_done_date': fields.Datetime.now()
                })
        
        return True
    
    def action_finalize_job(self):
        """Finalize job and trigger maintenance schedule if applicable"""
        for job in self:
            if job.state != 'work_order':
                raise UserError(_('Job must be in Work Order state to finalize.'))
            
            if not job.work_order_done_date:
                raise UserError(_('Please mark the work order as done first before finalizing the job.'))
            
            # Update end date
            job.write({
                'state': 'done',
                'end_date': fields.Datetime.now()
            })
            
            # Create maintenance record if this is a maintenance job
            if job.is_maintenance and job.periodic_maintenance_interval:
                job._create_maintenance_record()
        
        return True
    
    def _create_maintenance_record(self):
        """Create maintenance record when job is finalized"""
        self.ensure_one()
        if not self.next_maintenance_date:
            return
        
        maintenance = self.env['auto.vehicle.repair.maintenance'].create({
            'vehicle_id': self.vehicle_id.id,
            'customer_id': self.customer_id.id,
            'related_job_id': self.id,
            'scheduled_maintenance_date': self.next_maintenance_date,
            'status': 'pending',
        })
        
        self.write({'maintenance_record_id': maintenance.id})
        return maintenance
    
    def action_cancel(self):
        """Cancel job"""
        for job in self:
            if job.state in ('done', 'cancelled'):
                raise UserError(_('Cannot cancel a job that is already done or cancelled.'))
            job.write({'state': 'cancelled'})
        return True
    
    def action_reset_to_inspection(self):
        """Reset job to inspection state"""
        for job in self:
            if job.state == 'done':
                raise UserError(_('Cannot reset a completed job.'))
            job.write({
                'state': 'inspection',
                'approval_status': 'pending'
            })
        return True
    
    @api.constrains('quotation_amount')
    def _check_quotation_amount(self):
        for job in self:
            if job.quotation_amount and job.quotation_amount < 0:
                raise ValidationError(_('Quotation amount cannot be negative.'))
    
    # Computed fields for reports
    engine_condition_label = fields.Char(compute='_compute_selection_labels', store=False)
    brakes_condition_label = fields.Char(compute='_compute_selection_labels', store=False)
    tires_condition_label = fields.Char(compute='_compute_selection_labels', store=False)
    electrical_condition_label = fields.Char(compute='_compute_selection_labels', store=False)
    body_condition_label = fields.Char(compute='_compute_selection_labels', store=False)
    overall_condition_label = fields.Char(compute='_compute_selection_labels', store=False)
    
    @api.depends('engine_condition', 'brakes_condition', 'tires_condition', 'electrical_condition', 'body_condition', 'overall_condition')
    def _compute_selection_labels(self):
        """Compute human-readable labels for selection fields"""
        for job in self:
            # Engine condition
            engine_selection = [('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'), ('critical', 'Critical')]
            job.engine_condition_label = dict(engine_selection).get(job.engine_condition, 'N/A')
            
            # Brakes condition
            brakes_selection = [('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'), ('critical', 'Critical')]
            job.brakes_condition_label = dict(brakes_selection).get(job.brakes_condition, 'N/A')
            
            # Tires condition
            tires_selection = [('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'), ('critical', 'Critical')]
            job.tires_condition_label = dict(tires_selection).get(job.tires_condition, 'N/A')
            
            # Electrical condition
            electrical_selection = [('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'), ('critical', 'Critical')]
            job.electrical_condition_label = dict(electrical_selection).get(job.electrical_condition, 'N/A')
            
            # Body condition
            body_selection = [('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor')]
            job.body_condition_label = dict(body_selection).get(job.body_condition, 'N/A')
            
            # Overall condition
            overall_selection = [('excellent', 'Excellent'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'), ('critical', 'Critical')]
            job.overall_condition_label = dict(overall_selection).get(job.overall_condition, 'N/A')

