from app import db, models

def create_parking_lot(number_of_slots):
    """
    Creates the parking lot

    Parameters:
    number_of_slots (int): The number of parking slots

    Returns:
    int: number of slots created
    """
    # Check if the parking lot is already created or not. If yes, drop and create again.
    if models.Slot.query.count() > 0:
        models.Slot.query.delete()
        models.Parking.query.delete()

    for slot in xrange(1, number_of_slots+1):
        db.session.add(models.Slot(id=slot))
        db.session.commit()

    return number_of_slots

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
    int: Slot number of the parked vehicle or -1 (Not found)
    """

    parking_slot = models.Parking.query.order_by(models.Parking.slot_id).filter(models.Parking.active.is_(True), models.Parking.registration_number==registration_number).first()

    return parking_slot.slot_id if parking_slot else -1

def process_command_input(command_input):
    """
    Processes the input command from shell or file

    Parameters:
    command_input (string): The command given in the parking lot game

    Returns:
    0 or None
    """

    if command_input in ['exit', '']:
        return 0
    else:
        # Process the comman line input
        command_inputs = command_input.split()

        if command_inputs[0] == 'create_parking_lot': # create_parking_lot
            message = 'Created a parking lot with {} slots'.format(create_parking_lot(int(command_inputs[1])))
        elif command_inputs[0] == 'park':             # Park car
            slot_id = park_vehicle(command_inputs[1], command_inputs[2])
            if slot_id == -2:
                message = 'This is a repeated parking. Car already in parking.'
            elif slot_id == -1:
                message =  'Sorry, parking lot is full'
            else:
                message =  'Allocated slot number: {}'.format(slot_id)
        elif command_inputs[0] == 'leave':           # Unpark car
            message = 'Slot number {} is free'.format(int(command_inputs[1])) if unpark_vehicle(int(command_inputs[1])) else 'The parking slot is inactive'
        elif command_inputs[0] == 'status':          # Parking lot status
            parking_slots_status = parking_lot_status()
            if parking_slots_status:
                message = 'Slot No.    Registration No    Colour'
                for parking_slot_status in parking_slots_status:
                    message =  '{}\n{}           {}      {}'.format(message, parking_slot_status['slot_id'], parking_slot_status['registration_number'], parking_slot_status['colour'])
            else:
                message = 'Parking Lot is empty'
        elif command_inputs[0] == 'registration_numbers_for_cars_with_colour': # registration_numbers_for_cars_with_colour
            registration_numbers = info_for_vehicles_with_colour(command_inputs[1], 'registration_number')
            message = ', '.join(registration_numbers) if registration_numbers else 'Not found'
        elif command_inputs[0] == 'slot_numbers_for_cars_with_colour':         # slot_numbers_for_cars_with_colour
            slot_numbers = info_for_vehicles_with_colour(command_inputs[1], 'slot_id')
            message = ', '.join(map(str, slot_numbers)) if slot_numbers else 'Not found'
        elif command_inputs[0] == 'slot_number_for_registration_number':       # slot_number_for_registration_number
            slot_id = slot_number_for_registration_number(command_inputs[1])
            message = 'Not found' if slot_id == -1 else '{}'.format(slot_id)
        else:
            message = 'Invalid Command'
        return message
