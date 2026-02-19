from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class H_JubranProject(models.Model):
    _name = 'h_jubran.project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Project'
    _order = 'id desc'

    # === Basic Metadata ===
    name = fields.Char(string='Project Name', required=True)
    code = fields.Char(string='Project Code', copy=False, readonly=True)
    description = fields.Text(string='Description / Objectives')

    client_id = fields.Many2one('res.partner', string='Customer', domain=[('is_company', '=', True)])
    project_manager_id = fields.Many2one('res.users', string='Project Manager', required=False)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date')
    budget = fields.Monetary(string='Project Budget', currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id.id
    )

    # === Link to Structure (formerly project_type) ===
    structure_id = fields.Many2one(
        'h_jubran.project.structure.global',
        string='Project Structure Type',
        required=False,
        help='Select a predefined structure containing stages and elements.'
    )

    stage_line_ids = fields.One2many(
        'h_jubran.project.stage.line',
        'project_id',
        string='Project Stages and Elements',
        readonly=True
    )

    # === Lifecycle Tracking ===
    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'In Progress'),
        ('done', 'Done'),        
    ], string='Status', default='draft', tracking=True)

    progress = fields.Float(
        string='Overall Progress (%)',
        compute='_compute_overall_progress',
        store=True
    )

    attachment_ids = fields.Many2many(
        'ir.attachment',
        'project_attachment_rel',
        'project_id',
        'attachment_id',
        string='Attachments'
    )
    
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        readonly=True, # Prevent manual changes after creation
        copy=False,
        ondelete='restrict',
        help="The analytic account used to track costs and revenues for this project."
    )
    
    # site = fields.Char(
    #     string='Site (Location)',
    #     required=False,
    #     help='Specify the project site or location.'
    # )
    
    site = fields.Many2one(
        'stock.location',
        string='Project Site (Location)',
        required=False,
        ondelete='restrict',
        help='The physical location or warehouse associated with the project.'
    )

    boq_summary_ids = fields.One2many(
        'h_jubran.boq.summary',
        'project_id',
        string='BOQ Summaries'
    )
    boq_summary_count = fields.Integer(
        string='BOQ Summary Count',
        compute='_compute_boq_summary_count'
    )

    # === Computed Fields ===
    @api.depends('stage_line_ids.progress')
    def _compute_overall_progress(self):
        for project in self:
            if not project.stage_line_ids:
                project.progress = 0.0
            else:
                total = sum(stage.progress for stage in project.stage_line_ids)
                project.progress = total / len(project.stage_line_ids)

    # === Core Logic ===
    # @api.model
    # def create(self, vals):
    #     record = super().create(vals)
    #     current_year = datetime.now().year
    #     record.code = f"PRJ-{current_year}-{record.id:04d}"

    #     return record
    
    # Override the create method
    @api.model
    def create(self, vals):
        # 1. Create the project record first
        record = super().create(vals)        
        # 2. Set the project code
        current_year = datetime.now().year
        record.code = f"PRJ-{current_year}-{record.id:04d}"
        
        """The codes below are to activate the linking of a Project to the Account analytics Model but they are commented out for now"""
        # === FIX: Find the mandatory analytic plan ID ===
        # AnalyticPlan = self.env['account.analytic.plan']
        # # Search for the first active analytic plan in the database
        # plan = AnalyticPlan.search([], limit=1)
        # if not plan:
        #     # If no Analytic Plan exists, raise an informative error to the user/admin
        #     raise UserError(_("Analytic Plan (account.analytic.plan) is required but none found. Please configure a plan in Accounting settings."))

        # # 3. Create the corresponding Analytic Account
        # analytic_vals = {
        #     'name': f"{record.name} ({record.code})",
        #     'code': record.code,
        #     'custom_project_id': record.id, #Thisis the name i called it in the custom models i created for it
        #     # === MANDATORY FIELD ADDED ===
        #     'plan_id': plan.id,
        #     # =============================
        # }        
        # analytic_account = self.env['account.analytic.account'].create(analytic_vals)        
        # # 4. Link the newly created Analytic Account to the project
        # record.analytic_account_id = analytic_account.id        
        return record

    def _compute_boq_summary_count(self):
        for project in self:
            project.boq_summary_count = len(project.boq_summary_ids)

    def action_view_boq_summaries(self):
        self.ensure_one()
        action = self.env.ref('h_jubran_prd.action_h_jubran_boq_summary').read()[0]
        action['domain'] = [('project_id', '=', self.id)]
        action['context'] = {
            'default_project_id': self.id,
            'search_default_project_id': self.id,
        }
        return action


    def action_generate_structure(self):
        """Populate stages and elements from the selected structure."""
        for project in self:
            if not project.structure_id:
                raise UserError(_("Please select a Project Structure before generating."))

            # 1. Prepare the commands for the stage_line_ids One2many field.
            commands = []
            
            # DELETE COMMAND: (5, 0, 0) tells Odoo to delete all existing records.
            commands.append((5, 0, 0))
            
            # CREATE COMMANDS: (0, 0, values) for each new record
            for line in project.structure_id.line_ids:
                commands.append((0, 0, {
                    'stage_id': line.stage_id.id,
                    'responsible_id': project.project_manager_id.id,
                    # (6, 0, IDs) command to set the many2many values (clear and replace)
                    'element_ids': [(6, 0, line.element_ids.ids)], 
                }))
            
            # 2. EXECUTE: Assign the full command list to the One2many field
            project.stage_line_ids = commands
            
            # Set state to 'in_progress' or 'approved' if it was 'draft'
            if project.state == 'draft':
                 project.action_submit_for_approval() 


    # === Lifecycle Transitions ===
    def action_draft(self):
        self.write({'state': 'draft'})

    def action_progress(self):
        self.write({'state': 'progress'})

    def action_done(self):
        self.write({'state': 'done'})
    
    # === Analytic Helpers (required by project_purchase/project_stock modules) ===
    def _get_analytic_distribution(self):
        """Return analytic distribution used by purchase/accounting integrations.

        Odoo's enterprise ``project_purchase`` module expects projects to define
        an analytic distribution that can be applied automatically on purchase
        order lines.  Our custom project model does not yet create analytic
        accounts, so we gracefully fallback to an empty distribution when no
        analytic account is configured.
        """
        self.ensure_one()
        if self.analytic_account_id:
            # Full distribution on the linked analytic account
            return {self.analytic_account_id.id: 100}
        return {}

# =======================================================================
# Stage and Element Models
# =======================================================================

class H_JubranProjectStageLine(models.Model):
    _name = 'h_jubran.project.stage.line'
    _description = 'Project Stage Line'

    project_id = fields.Many2one('h_jubran.project', string='Project', ondelete='cascade')
    stage_id = fields.Many2one('h_jubran.project.stage.global', string='Stage', required=True)
    
    responsible_id = fields.Many2one('res.users', string='Responsible Person')
    planned_start_date = fields.Date(string='Planned Start Date')
    planned_end_date = fields.Date(string='Planned End Date')

    # element_ids = fields.Many2many(
    #     'h_jubran.structure.element',
    #     # Removed explicit table name to force Odoo to create a new, clean junction table.
    #     # Odoo will now auto-generate a name for the M2M table.
    #     string='Stage Elements'
    # )

    # material_ids = fields.Many2many(
    #     'product.product',
    #     'project_stage_material_rel',
    #     'stage_line_id',
    #     'product_id',
    #     string='Linked Materials'
    # )

    # task_ids = fields.One2many(
    #     'project.task',
    #     'stage_line_id',
    #     string='Linked Tasks'
    # )

    progress = fields.Float(
        string='Stage Progress (%)',
        compute='_compute_stage_progress',
        store=True
    )

    state = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ], string='Stage Status', default='not_started')

    # @api.depends('element_ids.progress')
    # def _compute_stage_progress(self):
    #     for stage in self:
    #         if not stage.element_ids:
    #             stage.progress = 0.0
    #         else:
    #             total = sum(e.progress for e in stage.element_ids)
    #             stage.progress = total / len(stage.element_ids)


class H_JubranStructureElement(models.Model):
    _name = 'h_jubran.structure.element'
    _description = 'Project Structure Element'

    name = fields.Char(string='Element Name', required=True)
    description = fields.Text(string='Description')
    progress = fields.Float(string='Progress (%)', default=0.0)

    responsible_id = fields.Many2one('res.users', string='Assigned To')
    remarks = fields.Text(string='Remarks')
