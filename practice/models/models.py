# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SchoolSubject(models.Model):
    _name = "practice.subject"
    _description = "School Subject"

    name = fields.Char(string="Subject Name", required=True)
    code = fields.Char(string="Subject Code")
    description = fields.Text(string="Description")


class SchoolUser(models.Model):
    _inherit = "res.partner"

    date_of_birth = fields.Date(string="Date of Birth")


class Classroom(models.Model):
    _name = "practice.classroom"
    _description = "Classroom Model"

    name = fields.Char(string="Classroom Name", required=True)
    capacity = fields.Integer(string="Class Capacity", default=30)
    teacher_id = fields.Many2one("practice.teacher", string="Assigned Teacher")
    student_ids = fields.Many2many("practice.student", string="Enrolled Students")
    average_cgpa = fields.Float(
        string="Average GPA", compute="_compute_avg_cgpa", store=True
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("ongoing", "Ongoing"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        string="Status",
    )

    @api.depends("student_ids.gpa")
    def _compute_avg_cgpa(self):
        for classroom in self:
            students = classroom.student_ids
            if students:
                total = sum(students.mapped("gpa"))
                classroom.average_cgpa = total / len(students)
            else:
                classroom.average_cgpa = 0.0

    @api.constrains("student_ids", "capacity")
    def _check_capacity(self):
        for classroom in self:
            if len(classroom.student_ids) > classroom.capacity:
                raise ValidationError("Classroom capacity exceeded.")


class Student(models.Model):
    _name = "practice.student"
    _description = "Student Model for Our Schema"
    _rec_name = "partner_id"

    gpa = fields.Float(string="GPA", default=0.0)
    is_border = fields.Boolean(string="Boarding Student", default=False)
    subject_ids = fields.Many2many("practice.subject", string="Registered Subjects")
    classroom_id = fields.Many2one(
        "practice.classroom", compute="_compute_classroom", string="My Classroom"
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Student Profile",
        ondelete="cascade",
        required=True,
    )
    guarantor_id = fields.Many2one(
        "res.partner", string="Guarantor", ondelete="restrict", required=True
    )

    _sql_constraints = [
        (
            "partner_id_constraint",
            "unique(partner_id)",
            "A user already references that profile",
        )
    ]

    def _compute_classroom(self):
        for record in self:
            # Finds the first classroom where this student is enrolled
            classroom = self.env["practice.classroom"].search(
                [("student_ids", "in", record.id)], limit=1
            )
            record.classroom_id = classroom


class Teacher(models.Model):
    _name = "practice.teacher"
    _description = "Teacher Model for Our Schema"
    _rec_name = "partner_id"

    subject_ids = fields.Many2many("practice.subject", string="Subjects Assigned")
    classroom_ids = fields.One2many(
        "practice.classroom", "teacher_id", string="My Classrooms"
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Teacher Profile",
        ondelete="cascade",
        required=True,
    )

    _sql_constraints = [
        (
            "partner_id_constraint",
            "unique(partner_id)",
            "A user already references that profile",
        )
    ]
