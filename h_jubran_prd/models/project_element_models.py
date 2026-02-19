from odoo import fields, models

class H_JubranProjectElementGlobal(models.Model):
    _name = 'h_jubran.project.element.global'
    _description = 'Central Repository of Project Elements (Costing Items)'
    _order = 'name'

    name = fields.Char(string='Element Name', required=True)
    code = fields.Char(string='Code', copy=False, help="Auto-generated unique identifier for the element.")
    description = fields.Text(string='Description')
    is_active = fields.Boolean(string='Active', default=True)
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'The Element Code must be unique!')
    ]

    # @api.model
    # def create(self, vals):
    #     record = super(H_JubranProjectElementGlobal, self).create(vals)
    #     record.code = f"PRE-{record.id:04d}" #E here shows that it is Element
    #     return record
