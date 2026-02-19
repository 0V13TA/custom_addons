# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MaintenanceRecord(models.Model):
    _name = 'auto.vehicle.repair.maintenance'
    _description = 'Maintenance Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'scheduled_maintenance_date asc'

    name = fields.Char(
        string='Maintenance Reference',
        required=True,
        index=True,
        default=lambda self: _('New'),
        tracking=True,
        help='Maintenance record reference'
    )
    vehicle_id = fields.Many2one(
        'auto.vehicle.repair.vehicle',
        string='Vehicle',
        required=True,
        tracking=True,
        ondelete='restrict',
        help='Vehicle scheduled for maintenance'
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        tracking=True,
        related='vehicle_id.owner_id',
        store=True,
        readonly=True,
        help='Customer who owns the vehicle'
    )
    related_work_order_id = fields.Many2one(
        'auto.vehicle.repair.work.order',
        string='Related Work Order',
        tracking=True,
        help='Work order that generated this maintenance record'
    )
    scheduled_maintenance_date = fields.Date(
        string='Scheduled Maintenance Date',
        required=True,
        tracking=True,
        help='Date when maintenance is scheduled'
    )
    status = fields.Selection([
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='pending', required=True, tracking=True,
        help='Status of the maintenance record')
    
    completed_date = fields.Date(
        string='Completed Date',
        tracking=True,
        help='Date when maintenance was completed'
    )
    notes = fields.Text(string='Notes')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('auto.vehicle.repair.maintenance') or _('New')
        return super().create(vals_list)
    
    def action_mark_completed(self):
        """Mark maintenance as completed"""
        for record in self:
            if record.status == 'completed':
                raise ValidationError(_('This maintenance record is already completed.'))
            record.write({
                'status': 'completed',
                'completed_date': fields.Date.today()
            })
        return True
    
    def action_mark_pending(self):
        """Mark maintenance as pending"""
        for record in self:
            record.write({
                'status': 'pending',
                'completed_date': False
            })
        return True
    
    def action_cancel(self):
        """Cancel maintenance record"""
        for record in self:
            record.write({'status': 'cancelled'})
        return True
    
    def action_create_inspection(self):
        """Create a new inspection from this maintenance record"""
        self.ensure_one()
        inspection = self.env['auto.vehicle.repair.inspection'].create({
            'vehicle_id': self.vehicle_id.id,
            'inspection_notes': f'Maintenance scheduled for {self.scheduled_maintenance_date}',
            'is_maintenance': True,
            'state': 'draft',
        })
        return {
            'name': _('Inspection'),
            'type': 'ir.actions.act_window',
            'res_model': 'auto.vehicle.repair.inspection',
            'view_mode': 'form',
            'res_id': inspection.id,
            'target': 'current',
        }
    
    @api.constrains('scheduled_maintenance_date')
    def _check_scheduled_date(self):
        for record in self:
            if record.scheduled_maintenance_date and record.scheduled_maintenance_date < fields.Date.today() and record.status == 'pending':
                # Allow past dates but warn - this is just a constraint, not blocking
                pass

