from app import db
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    mimetype = db.Column(db.String(255), nullable=False)