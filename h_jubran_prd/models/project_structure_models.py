from odoo import models, fields, api
from odoo.exceptions import ValidationError


class H_JubranProjectStructureGlobal(models.Model):
    _name = 'h_jubran.project.structure.global'
    _description = 'Project Structure Global'
    _order = 'id desc'

    name = fields.Char(string='Structure Name', required=True)
    stage_number = fields.Integer(
        string='Number of Stages',
        required=True,
        help='Maximum number of stages allowed for this structure'
    )
    description = fields.Text(string='Description')

    line_ids = fields.One2many(
        'h_jubran.project.structure.line',
        'structure_id',
        string='Stages and Elements',
        help='List of stages and their corresponding elements'
    )
    

    @api.constrains('line_ids')
    def _check_stage_limit(self):
        for record in self:
            if record.stage_number and len(record.line_ids) > record.stage_number:
                raise ValidationError(
                    f"You cannot add more than {record.stage_number} stage(s) to this structure."
                )




class H_JubranProjectStructureLine(models.Model):
    _name = 'h_jubran.project.structure.line'
    _description = 'Project Structure Line (Stage & Elements)'

    structure_id = fields.Many2one(
        'h_jubran.project.structure.global',
        string='Project Structure',
        ondelete='cascade'
    )

    stage_id = fields.Many2one(
        'h_jubran.project.stage.global',
        string='Stage',
        required=True
    )

    element_ids = fields.Many2many(
        'h_jubran.project.element.global',
        'h_jubran_structure_line_element_rel',
        'line_id', 'element_id',
        string='Elements'
    )

    note = fields.Char(string='Note')

    _sql_constraints = [
        ('unique_stage_per_structure', 'unique(structure_id, stage_id)', 'This stage already exists in the structure!')
    ]
