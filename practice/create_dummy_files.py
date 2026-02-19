# -*- coding: utf-8 -*-
# Run this in Odoo shell for large dummy dataset (no dependencies)

import random

# ---------- Subjects ----------
subject_names = [
    "Mathematics",
    "English",
    "Physics",
    "Chemistry",
    "History",
    "Biology",
    "Geography",
    "Computer Science",
    "Art",
    "Music",
]

subject_records = []
for i, name in enumerate(subject_names, 1):
    subject = env["practice.subject"].create(
        {
            "name": name,
            "code": f"{name[:4].upper()}{100 + i}",
            "description": f"{name} course description",
        }
    )
    subject_records.append(subject)

# ---------- Partners ----------
student_names = [
    "Alice Johnson",
    "Bob Smith",
    "Charlie Brown",
    "Diana Prince",
    "Edward King",
    "Fiona Clarke",
    "George White",
    "Hannah Lee",
    "Ian Black",
    "Julia Green",
]

teacher_names = ["Laura Adams", "Michael Scott", "Nancy Drew"]

partner_records = []

# Students
for i, name in enumerate(student_names):
    email = name.lower().replace(" ", ".") + "@example.com"
    partner = env["res.partner"].create(
        {
            "name": name,
            "email": email,
            "date_of_birth": f"200{random.randint(3, 6)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
        }
    )
    partner_records.append({"partner": partner, "type": "student"})

# Teachers
for name in teacher_names:
    email = name.lower().replace(" ", ".") + "@example.com"
    partner = env["res.partner"].create(
        {
            "name": name,
            "email": email,
            "date_of_birth": f"19{random.randint(70, 90)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
        }
    )
    partner_records.append({"partner": partner, "type": "teacher"})

# ---------- Teachers ----------
teacher_records = []
teacher_partners = [p["partner"] for p in partner_records if p["type"] == "teacher"]

for partner in teacher_partners:
    subjects = random.sample(subject_records, k=random.randint(2, 4))
    teacher = env["practice.teacher"].create(
        {"partner_id": partner.id, "subject_ids": [(6, 0, [s.id for s in subjects])]}
    )
    teacher_records.append(teacher)

# ---------- Students ----------
student_records = []
student_partners = [p["partner"] for p in partner_records if p["type"] == "student"]

for partner in student_partners:
    guarantor = random.choice(teacher_partners)
    subjects = random.sample(subject_records, k=random.randint(2, 5))
    student = env["practice.student"].create(
        {
            "partner_id": partner.id,
            "guarantor_id": guarantor.id,
            "gpa": round(random.uniform(2.0, 4.0), 2),
            "is_border": random.choice([True, False]),
            "subject_ids": [(6, 0, [s.id for s in subjects])],
        }
    )
    student_records.append(student)

# ---------- Classrooms ----------
classroom_records = []

for i in range(1, 4):
    teacher = random.choice(teacher_records)
    students_in_class = random.sample(student_records, k=random.randint(3, 6))
    classroom = env["practice.classroom"].create(
        {
            "name": f"Class {chr(64 + i)}",
            "capacity": 30,
            "teacher_id": teacher.id,
            "student_ids": [(6, 0, [s.id for s in students_in_class])],
            "state": random.choice(["draft", "ongoing", "completed"]),
        }
    )
    classroom_records.append(classroom)

print("Dummy dataset created successfully (no external dependencies)!")
