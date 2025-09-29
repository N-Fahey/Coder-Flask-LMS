from datetime import date

from init import db

class Enrolment(db.Model):
    __tablename__ = 'enrolments'
    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', name="enrolments_unique_student_course"),
    )
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    enrolment_date = db.Column(db.Date, default=date.today)

    student = db.relationship('Student', back_populates='enrolments')
    course = db.relationship('Course', back_populates='enrolments')
