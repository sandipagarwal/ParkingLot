from app import db

class Slot(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # (Re-)Using the PK (id) for slot numbers
    parkings = db.relationship('Parking', backref='slot', lazy=True)
    active = db.Column(db.Boolean, default=True, nullable=False)  # A slot can be marked

    def __repr__(self):
        return '{}'.format(self.id)


class Parking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slot_id = db.Column(db.Integer, db.ForeignKey('slot.id'), nullable=False)
    registration_number = db.Column(db.String(20), nullable=False, index=True)  # Longest registration number is assumed to be of max length 20 including '-'
    colour = db.Column(db.String(15), nullable=False, index=True)  # Colour length assumed to be max 15
    active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return '{}'.format(self.registration_number)
