from app import db, models

def create_parking_lot(number_of_slots):
    """
    Creates the parking lot

    Parameters:
    number_of_slots (int): The number of parking slots
    """
    # TODO: Check if the parking is already created or not. If yes, drop and create again.

    for slot in xrange(number_of_slots):
        db.session.add(models.Slot(id=slot + 1))
        db.session.commit()

def park_vehicle(registration_number, colour):
    """
    Parks the vehicle

    Parameters:
    registration_number (string): The registration number of the vehicle (car in our project)
    colour (string): The colour of the vehicle

    Returns:
    int: Slot number or -1 for "parking lot full" or -2 for "repeated parking"
    """
    # Check if the vehicle is already parked and not repeated parking
    repeated_parking = models.Parking.query.filter(models.Parking.active.is_(True), models.Parking.registration_number==registration_number).first()
    if repeated_parking:
        slot_id = -2
    else:
        # Find the available slot
        occupied_slots = zip(*db.session.query(models.Slot.id).outerjoin(models.Parking).filter(models.Parking.active.is_(True), models.Slot.active.is_(True)).all())
        slot = models.Slot.query.order_by(models.Slot.id).filter(~models.Slot.id.in_(occupied_slots[0] if occupied_slots else [])).first()

        # Park the vehicle in the available slot
        if slot:
            slot_id = slot.id
            db.session.add(models.Parking(slot_id=slot_id, registration_number=registration_number, colour=colour))
            db.session.commit()
        else:
            slot_id = -1
    return slot_id

def unpark_vehicle(slot_id):
    """
    Parks the vehicle

    Parameters:
    slot_id (int): The slot id that needs to be unparked

    Returns:
    Boolean: True, if the parking slot was successfully unparked as a outcome of this operation. False, if the spot is inactive
    """
    if models.Slot.query.filter(models.Slot.active.is_(True), models.Slot.id==slot_id).first():
        models.Parking.query.filter_by(slot_id=slot_id).update(dict(active=False))
        db.session.commit()
        return True
    else:
        return False
