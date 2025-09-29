from init import db

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    duration = db.Column(db.Float)

    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"), nullable=False)

    teacher = db.relationship('Teacher', back_populates='courses')
    enrolments = db.relationship('Enrolment', back_populates='course')
    