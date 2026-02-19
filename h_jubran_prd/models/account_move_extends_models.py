from odoo import fields, models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Project Link (Many2one to your Project model)
    project_id = fields.Many2one(
        'h_jubran.project', 
        string='Project',
        tracking=True, 
        help='The main project linked to this invoice or bill.'
    )
    
    project_site = fields.Many2one(
        'stock.location',
        string='Project Site (Location)',
        readonly=False,
        store=True,
        help="Site/Location of the linked project."
    )

    
    #Onchange Method for Site Auto-population
    # This logic executes when the project_id is changed
    @api.onchange('project_id')
    def _onchange_project_id_site(self):
        if self.project_id:
            # Set the site to the project's site field
            self.project_site = self.project_id.site
            
            # Optionally, you can also auto-set the analytic account if not using compute/related
            # self.analytic_account_id = self.project_id.analytic_account_id 
            
        else:
            # Clear the site if no project is selected
            self.project_site = False
            
    
    # Stage Link (Many2one to your Global Stage model)
    # This field is generally not strictly needed on the header, but useful for filtering.
    # We will primarily focus on the line items for stages.
    # stage_id = fields.Many2one(
    #     'h_jubran.project.stage.global', 
    #     string='Project Stage', 
    #     tracking=True
    # )

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Project Link: Inherits from the header and is available for reporting
    project_id = fields.Many2one(
        'h_jubran.project', 
        string='Project',
        store=True, 
        readonly=True, 
        related='move_id.project_id' # Automatically populated from the Invoice header
    )

    # Stage Link: This is the crucial field for detailed tracking on the line item level
    stage_id = fields.Many2one(
        'h_jubran.project.stage.global', 
        string='Project Stage',
        domain="[('id', 'in', allowed_stage_ids)]", # Apply dynamic domain
        help='The specific project stage related to this line item cost/revenue.'
    )
    
    substage_id = fields.Many2one(
        'h_jubran.project.stage.global',
        string='Substage',
        help="A granular phase within the stage."
    )
    
    element_id = fields.Many2one(
        'h_jubran.project.element.global',
        string='Element',
        help="The specific element within the stage this purchase relates to."
    )
    
    # Technical field for dynamic domain filtering on stages
    allowed_stage_ids = fields.Many2many(
        'h_jubran.project.stage.global', 
        compute='_compute_allowed_stage_ids'
    )

    def _compute_allowed_stage_ids(self):
        """
        Calculates the stages available for selection on the line item.
        If a project is selected on the Invoice/Bill, only the stages present 
        in that project's structure should be selectable.
        """
        for line in self:
            if line.project_id:
                # Get the stage IDs from the project's stage_line_ids
                project_stage_lines = self.env['h_jubran.project.stage.line'].search([
                    ('project_id', '=', line.project_id.id)
                ])
                stage_ids = project_stage_lines.stage_id.ids
                line.allowed_stage_ids = [(6, 0, stage_ids)]
            else:
                # If no project is selected, allow all active stages (or restrict to empty)
                line.allowed_stage_ids = self.env['h_jubran.project.stage.global'].search([('is_active', '=', True)]).ids
                
    
    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        """Clear substage and element when the main stage changes."""
        self.substage_id = False
        self.element_id = False