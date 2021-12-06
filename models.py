
from app import db

class Leaf(db.Model):
    __tablename__ = 'leafs'

    id = db.Column(db.Integer, primary_key=True)
    estate_name = db.Column(db.String())
    manage_name = db.Column(db.String())
    asst_manager_name = db.Column(db.String())
    slot_no = db.Column(db.String())

    def __init__(self, name, author, published):
        self.estate_name = estate_name
        self.manage_name = manage_name
        self.asst_manager_name = asst_manager_name
        self.slot_no = slot_no

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.estate_name, 
            'name': self.manage_name,
            'author': self.asst_manager_name,
            'published':self.slot_no
        }