# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HjubranPrMakePurchaseOrder(models.TransientModel):
    _name = 'h_jubran.pr.make.purchase.order'
    _description = 'Make Purchase Order from Purchase Request'

    item_ids = fields.One2many(
        'h_jubran.pr.make.purchase.order.item',
        'wiz_id',
        string='Items'
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids', [])
        
        if active_model == 'h_jubran.purchase.request.line':
            lines = self.env[active_model].browse(active_ids)
            items = []
            for line in lines:
                if line.pending_qty_to_receive > 0:
                    items.append((0, 0, {
                        'line_id': line.id,
                        'product_id': line.product_id.id if line.product_id else False,
                        'name': line.name or '',
                        'product_qty': line.pending_qty_to_receive,
                        'product_uom_id': line.product_uom_id.id if line.product_uom_id else False,
                    }))
            res['item_ids'] = items
        return res

    def make_purchase_order(self):
        """Create purchase order from selected purchase request lines"""
        self.ensure_one()
        
        if not self.item_ids:
            raise UserError(_("Please select at least one line to create purchase order."))
        
        # Group lines by vendor/partner
        partner_lines = {}
        for item in self.item_ids:
            pr_line = item.line_id
            # Get vendor from product or use default
            partner = False
            if pr_line.product_id and pr_line.product_id.seller_ids:
                partner = pr_line.product_id.seller_ids[0].partner_id
            else:
                # Use company partner or first vendor
                partner = self.env['res.partner'].search([('supplier_rank', '>', 0)], limit=1)
            
            if not partner:
                raise UserError(_("No vendor found for line: %s") % (pr_line.name or 'Untitled'))
            
            partner_id = partner.id
            if partner_id not in partner_lines:
                partner_lines[partner_id] = []
            partner_lines[partner_id].append(item)
        
        # Create purchase orders
        purchase_orders = self.env['purchase.order']
        for partner_id, items in partner_lines.items():
            po = self._create_purchase_order(partner_id, items)
            purchase_orders |= po
        
        # Return action to view created POs
        if len(purchase_orders) == 1:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'view_mode': 'form',
                'res_id': purchase_orders.id,
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', purchase_orders.ids)],
                'target': 'current',
            }

    def _create_purchase_order(self, partner_id, items):
        """Create a purchase order for a partner"""
        partner = self.env['res.partner'].browse(partner_id)
        pr = items[0].line_id.request_id
        
        # Get picking type
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'incoming'),
            ('warehouse_id.company_id', '=', self.env.company.id)
        ], limit=1)
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'incoming')
            ], limit=1)
        
        # Create PO
        po_vals = {
            'partner_id': partner_id,
            'picking_type_id': picking_type.id if picking_type else False,
            'origin': pr.name,
            'company_id': self.env.company.id,
        }
        
        # Copy project from PR
        if pr.project_id:
            po_vals['project_id'] = pr.project_id.id
        if pr.project_site:
            po_vals['project_site'] = pr.project_site.id
        
        po = self.env['purchase.order'].create(po_vals)
        
        # Create PO lines
        for item in items:
            pr_line = item.line_id
            line_vals = self._prepare_po_line(po, item, pr_line)
            po_line = self.env['purchase.order.line'].create(line_vals)
            
            # Link PR line to PO line
            pr_line.purchase_lines = [(4, po_line.id)]
        
        return po

    def _prepare_po_line(self, po, item, pr_line):
        """Prepare purchase order line values"""
        from odoo.tools import get_lang
        
        qty = item.product_qty
        if item.product_uom_id:
            qty = item.product_uom_id._compute_quantity(qty, item.product_uom_id)
        
        line_vals = {
            'order_id': po.id,
            'product_id': item.product_id.id if item.product_id else False,
            'product_uom': item.product_uom_id.id if item.product_uom_id else False,
            'product_qty': qty,
            'price_unit': pr_line.rate if pr_line.rate else 0.0,
            'name': item.name or pr_line.name or '',
            'date_planned': datetime.now(),
        }
        
        # Copy custom fields from PR line
        if pr_line.category_id:
            line_vals['category_id'] = pr_line.category_id.id
        if pr_line.subcategory_id:
            line_vals['subcategory_id'] = pr_line.subcategory_id.id
        if pr_line.master_element_id:
            line_vals['master_element_id'] = pr_line.master_element_id.id
        if pr_line.boq_rate:
            line_vals['boq_rate'] = pr_line.boq_rate
        
        return line_vals


class HjubranPrMakePurchaseOrderItem(models.TransientModel):
    _name = 'h_jubran.pr.make.purchase.order.item'
    _description = 'Purchase Request Line Item for PO Creation'

    wiz_id = fields.Many2one(
        'h_jubran.pr.make.purchase.order',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )
    line_id = fields.Many2one(
        'h_jubran.purchase.request.line',
        string='Purchase Request Line',
        required=True
    )
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(string='Description', required=True)
    product_qty = fields.Float(string='Quantity', required=True)
    product_uom_id = fields.Many2one('uom.uom', string='UoM')

