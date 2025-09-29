from flask import Blueprint

from init import db
from models import Student, Teacher, Course, Enrolment

cli_bp = Blueprint('db', __name__)

@cli_bp.cli.command('create')
def create_tables():
    db.create_all()
    print('Tables created.')

@cli_bp.cli.command('drop')
def drop_tables():
    db.drop_all()
    print('Tables dropped.')

@cli_bp.cli.command('seed')
def seed_tables():
    students = [
        Student(name='Alice', email='alice@email.com', address='Sydney'),
        Student(name='Bob', email='bob@example.com', address='Melbourne')
    ]
    teachers= [
        Teacher(name='Mr. Mike', department='IT', address='Sydney'),
        Teacher(name='Ms. Maddy', department='Science', address='Brisbane')
    ]
    db.session.add_all(students+teachers)
    db.session.commit()

    courses = [
        Course(name='IT 101', duration=1, teacher_id=teachers[0].id),
        Course(name='IT 102', duration=1.5, teacher_id=teachers[0].id),
        Course(name='IT 103', duration=1, teacher_id=teachers[0].id),
        Course(name='Physics', duration=3, teacher_id=teachers[1].id),
        Course(name='Biology', duration=2.5, teacher_id=teachers[1].id),
        Course(name='Chemistry', duration=2.5, teacher_id=teachers[1].id)
    ]

    db.session.add_all(courses)
    db.session.commit()

    enrolments = [
        Enrolment(enrolment_date='2025-09-24', student_id = students[0].id, course_id = courses[3].id),
        Enrolment(enrolment_date='2025-09-21', student_id = students[1].id, course_id = courses[0].id),
        Enrolment(enrolment_date='2025-09-15', student_id = students[1].id, course_id = courses[1].id),
        Enrolment(enrolment_date='2025-09-21', student_id = students[1].id, course_id = courses[2].id),
        Enrolment(enrolment_date='2025-09-26', student_id = students[0].id, course_id = courses[4].id),
        Enrolment(student_id = students[0].id, course_id = courses[5].id),
        Enrolment(student_id = students[0].id, course_id = courses[0].id)
    ]

    db.session.add_all(enrolments)
    db.session.commit()

    print('Tables seeded.')
