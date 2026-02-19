from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.model
    def _check_sale_module(self):
        """Check if sale module is installed"""
        return 'sale.order' in self.env.registry

    boq_summary_line_id = fields.Many2one(
        'h_jubran.boq.summary.line',
        string='BOQ Summary Line',
        ondelete='set null'
    )
    boq_number = fields.Char(string='BOQ Number')
    boq_code = fields.Char(string='BOQ Code')
    boq_scope = fields.Char(string='BOQ Scope')
    boq_category_id = fields.Many2one(
        'h_jubran.master.category',
        string='BOQ Category',
        ondelete='restrict'
    )
    boq_amount = fields.Monetary(
        string='BOQ Amount',
        currency_field='currency_id'
    )
    boq_actual_amount = fields.Monetary(
        string='BOQ Actual Amount',
        currency_field='currency_id'
    )

    def write(self, vals):
        result = super().write(vals)
        tracked_fields = {'boq_summary_line_id', 'boq_number', 'boq_code', 'boq_scope',
                          'boq_category_id', 'boq_amount', 'boq_actual_amount'}
        if tracked_fields.intersection(vals.keys()):
            self.mapped('boq_summary_line_id').invalidate_recordset([])
        return result

