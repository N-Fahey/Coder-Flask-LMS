from init import db

class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=True)

    courses = db.relationship('Course', back_populates='teacher', cascade='all, delete')
