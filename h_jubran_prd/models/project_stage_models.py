from odoo import fields, models, api

class H_JubranProjectStageGlobal(models.Model):
    _name = 'h_jubran.project.stage.global'
    _description = 'Central Repository of Project Stages'
    _order = 'name'

    name = fields.Char(string='Stage Name', required=True)
    code = fields.Char(string='Code', copy=False, help="Auto-generated unique identifier for the stage.")
    parent_stage_id = fields.Many2one(
        comodel_name='h_jubran.project.stage.global', 
        string='Parent Stage', 
        required=False,
        # --- CORRECTION 2: Apply Domain to show only non-sub-stages ---
        domain=[('is_sub_stage', '=', False)]
    )
    description = fields.Text(string='Description')
    is_active = fields.Boolean(string='Active', default=True)
    is_sub_stage = fields.Boolean(
        string='Is SubStage', 
        compute='_compute_is_sub_stage', 
        store=True, 
        default=False
    )

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'The Stage Code must be unique!')
    ]

    # @api.model
    # def create(self, vals):
    #     record = super(H_JubranProjectStageGlobal, self).create(vals)
    #     record.code = f"PRS-{record.id:04d}"  # S here shows that it is Element
    #     return record
    
    
    @api.depends('parent_stage_id')
    def _compute_is_sub_stage(self):
        """ Automatically sets is_sub_stage based on whether a parent is selected. """
        for record in self:
            # If parent_stage_id is set, it is a sub-stage.
            record.is_sub_stage = bool(record.parent_stage_id)
