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
    Unparks the vehicle

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

def parking_lot_status():
    """
    Status of the parking lot

    Parameters:
    None

    Returns:
    list: A list of dictionaries of parking slots data
    """

    parking_slots = []
    for parking_slot in models.Parking.query.order_by(models.Parking.slot_id).filter(models.Parking.active.is_(True)).all():
        parking_slots.append({
            "slot_id": parking_slot.slot_id,
            "registration_number": parking_slot.registration_number,
            "colour": parking_slot.colour,
        })
    return parking_slots

def info_for_vehicles_with_colour(colour, info):
    """
    Status of the parking lot

    Parameters:
    colour (string): The colour of the vehicle

    Returns:
    list: A list of registration numbers
    """

    return [
        getattr(parking_slot, info) for parking_slot in models.Parking.query.order_by(models.Parking.slot_id).filter(models.Parking.active.is_(True), models.Parking.colour.ilike(colour)).all()
    ]

def slot_number_for_registration_number(registration_number):
    """
    Status of the parking lot

    Parameters:
    registration_number (string): The registration number of the vehicle

    Returns:
    int: Slot number of the parked vehicle or -1
    """

    parking_slot = models.Parking.query.order_by(models.Parking.slot_id).filter(models.Parking.active.is_(True), models.Parking.registration_number==registration_number).first()

    return parking_slot.slot_id if parking_slot else -1
