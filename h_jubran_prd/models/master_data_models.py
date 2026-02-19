from odoo import fields, models, api


class HJubranMasterCategory(models.Model):
    _name = 'h_jubran.master.category'
    _description = 'Master Data Category'
    _order = 'code, name'

    name = fields.Char(required=True, string='Category Name')
    code = fields.Char(required=False, copy=False, string='Category Code')
    description = fields.Text(string='Description')
    subcategory_ids = fields.One2many(
        'h_jubran.master.subcategory',
        'category_id',
        string='Sub-Categories'
    )

    _sql_constraints = [
        ('h_jubran_master_category_code_unique', 'unique(code)', 'Category code must be unique.'),
    ]


class HJubranMasterSubCategory(models.Model):
    _name = 'h_jubran.master.subcategory'
    _description = 'Master Data Sub-Category'
    _order = 'code, name'

    name = fields.Char(required=True, string='Sub-Category Name')
    code = fields.Char(required=False, copy=False, string='Sub-Category Code')
    category_id = fields.Many2one(
        'h_jubran.master.category',
        string='Category',
        required=True,
        ondelete='cascade'
    )
    description = fields.Text(string='Description')
    element_ids = fields.One2many(
        'h_jubran.master.element',
        'subcategory_id',
        string='Elements'
    )
    
    # Quantity and Rate fields - updated from confirmed vendor bills
    quantity = fields.Float(
        string='Quantity',
        default=0.0,
        digits=(16, 2),
        help="Total quantity from all confirmed vendor bills for this subcategory"
    )
    
    rate = fields.Float(
        string='Rate',
        default=0.0,
        digits=(16, 2),
        help="Weighted average rate from all confirmed vendor bills for this subcategory"
    )

    _sql_constraints = [
        ('h_jubran_master_subcategory_code_unique', 'unique(code)', 'Sub-category code must be unique.'),
    ]


class HJubranMasterElement(models.Model):
    _name = 'h_jubran.master.element'
    _description = 'Master Data Element'
    _order = 'code, name'

    name = fields.Char(required=True, string='Element Name')
    code = fields.Char(required=True, copy=False, string='Element Code')
    subcategory_id = fields.Many2one(
        'h_jubran.master.subcategory',
        string='Sub-Category',
        required=True,
        ondelete='cascade'
    )
    category_id = fields.Many2one(
        'h_jubran.master.category',
        string='Category',
        store=True,
        readonly=True,
        related='subcategory_id.category_id'
    )
    description = fields.Text(string='Description')

    sub_element_ids = fields.One2many(
        'h_jubran.master.sub.element',
        'element_id',
        string='Sub-Elements'
    )

    _sql_constraints = [
        ('h_jubran_master_element_code_unique', 'unique(code)', 'Element code must be unique.'),
    ]


class HJubranMasterSubElement(models.Model):
    _name = 'h_jubran.master.sub.element'
    _description = 'Master Data Sub-Element'
    _order = 'code, name'

    name = fields.Char(required=True, string='Sub-Element Name')
    code = fields.Char(required=False, copy=False, string='Sub-Element Code')
    element_id = fields.Many2one(
        'h_jubran.master.element',
        string='Element',
        required=True,
        ondelete='cascade'
    )
    subcategory_id = fields.Many2one(
        'h_jubran.master.subcategory',
        string='Sub-Category',
        store=True,
        readonly=True,
        related='element_id.subcategory_id'
    )
    category_id = fields.Many2one(
        'h_jubran.master.category',
        string='Category',
        store=True,
        readonly=True,
        related='element_id.category_id'
    )
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('h_jubran_master_sub_element_code_unique', 'unique(code)', 'Sub-element code must be unique.'),
    ]

