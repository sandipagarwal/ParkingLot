import os
import unittest

from app import db, parking_lot, models, utils

class ParkingLotTests(unittest.TestCase):
    # TODO: This test class can be broken down into more classes and different files

    @classmethod
    def setUpClass(cls):
        # creates a test client
        cls.app = parking_lot.test_client()
        # propagate the exceptions to the test client
        cls.app.testing = True

        # Change config to test configs
        parking_lot.config['TESTING'] = True
        parking_lot.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(parking_lot.config['BASEDIR'], parking_lot.config['TEST_DB'])
        db.drop_all()

        cls.total_slots = 6

    @classmethod
    def tearDownClass(cls):
        db.drop_all()

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.drop_all()

    def test_create_parking_lot(self):

        # Create New Parking Lot
        self.assertEqual(utils.create_parking_lot(self.total_slots), self.total_slots)

        # Park
        self.assertEqual(utils.park_vehicle('KA-01-HH-1234', 'White'), 1)

        # Test count
        self.assertEqual(models.Parking.query.filter(models.Parking.active.is_(True)).count(), 1)

        # Test repeat call
        self.assertEqual(utils.create_parking_lot(self.total_slots), self.total_slots)

        # Test count
        self.assertEqual(models.Parking.query.filter(models.Parking.active.is_(True)).count(), 0)

    def test_park_vehicle(self):
        utils.create_parking_lot(self.total_slots)

        # Test initial count
        self.assertEqual(models.Parking.query.filter(models.Parking.active.is_(True)).count(), 0)

        # Test each slot allotment number
        self.assertEqual(utils.park_vehicle('KA-01-HH-1234', 'White'), 1)
        self.assertEqual(utils.park_vehicle('KA-01-HH-9999', 'White'), 2)
        self.assertEqual(utils.park_vehicle('KA-01-BB-0001', 'Black'), 3)
        self.assertEqual(utils.park_vehicle('KA-01-HH-7777', 'Red'), 4)
        self.assertEqual(utils.park_vehicle('KA-01-HH-2701', 'Blue'), 5)
        self.assertEqual(utils.park_vehicle('KA-01-HH-3141', 'Black'), 6)

        # Test final count
        self.assertEqual(models.Parking.query.filter(models.Parking.active.is_(True)).count(), self.total_slots)

    def test_repeated_park_vehicle(self):
        # Call test_park_vehicle to re-use code
        self.test_park_vehicle()

        # Test repeated parking
        self.assertEqual(utils.park_vehicle('KA-01-HH-1234', 'White'), -2)

        # Test no change in count
        self.assertEqual(models.Parking.query.filter(models.Parking.active.is_(True)).count(), self.total_slots)

    def test_park_vehicle_full_parking(self):
        # Call test_park_vehicle to re-use code
        self.test_park_vehicle()

        # Test full parking
        self.assertEqual(utils.park_vehicle('KA-01-HH-1235', 'White'), -1)

        # Test no change in count
        self.assertEqual(models.Parking.query.filter(models.Parking.active.is_(True)).count(), self.total_slots)

    def test_park_vehicle_first_empty(self):
        # Call test_park_vehicle to re-use code
        self.test_park_vehicle()

        # Unpark 4, 2, and 5
        self.assertTrue(utils.unpark_vehicle(4))
        self.assertTrue(utils.unpark_vehicle(2))
        self.assertTrue(utils.unpark_vehicle(5))

        # Test the count after unparking
        self.assertEqual(models.Parking.query.filter(models.Parking.active.is_(True)).count(), 3)

        # Park the vehicle
        self.assertEqual(utils.park_vehicle('KA-01-HH-1235', 'White'), 2)

        # Test the count after parking
        self.assertEqual(models.Parking.query.filter(models.Parking.active.is_(True)).count(), 4)

        # Complete the parking
        self.assertEqual(utils.park_vehicle('KA-01-HH-9999', 'White'), 4)
        self.assertEqual(utils.park_vehicle('KA-01-HH-7777', 'Red'), 5)

        # Test final count
        self.assertEqual(models.Parking.query.filter(models.Parking.active.is_(True)).count(), self.total_slots)

    def test_unpark_vehicle(self):
        # Call test_park_vehicle to re-use code
        self.test_park_vehicle()

        # Unpark 4, 2, and 5
        self.assertTrue(utils.unpark_vehicle(4))
        self.assertTrue(utils.unpark_vehicle(2))
        self.assertTrue(utils.unpark_vehicle(5))

        # Test the count after unparking
        self.assertEqual(models.Parking.query.filter(models.Parking.active.is_(True)).count(), 3)

        # Unpark the same slot
        self.assertTrue(utils.unpark_vehicle(4))

        # Test the count after unparking
        self.assertEqual(models.Parking.query.filter(models.Parking.active.is_(True)).count(), 3)

        # Unpark 100
        self.assertFalse(utils.unpark_vehicle(100))

        # Test the count after unparking
        self.assertEqual(models.Parking.query.filter(models.Parking.active.is_(True)).count(), 3)


    def test_parking_lot_status(self):
        # Initial empty parking lot
        self.assertEqual(utils.parking_lot_status(), [])

        # Call test_park_vehicle to re-use code
        self.test_park_vehicle()
        # Test full parking lot
        self.assertEqual(utils.parking_lot_status(), [
            {"slot_id": 1, "registration_number": "KA-01-HH-1234", "colour": "White"},
            {"slot_id": 2, "registration_number": "KA-01-HH-9999", "colour": "White"},
            {"slot_id": 3, "registration_number": "KA-01-BB-0001", "colour": "Black"},
            {"slot_id": 4, "registration_number": "KA-01-HH-7777", "colour": "Red"},
            {"slot_id": 5, "registration_number": "KA-01-HH-2701", "colour": "Blue"},
            {"slot_id": 6, "registration_number": "KA-01-HH-3141", "colour": "Black"},
        ])

        # Unpark 4, 2, and 5
        self.assertTrue(utils.unpark_vehicle(4))
        self.assertTrue(utils.unpark_vehicle(2))
        self.assertTrue(utils.unpark_vehicle(5))
        # Test partial parking lot
        self.assertEqual(utils.parking_lot_status(), [
            {"slot_id": 1, "registration_number": "KA-01-HH-1234", "colour": "White"},
            {"slot_id": 3, "registration_number": "KA-01-BB-0001", "colour": "Black"},
            {"slot_id": 6, "registration_number": "KA-01-HH-3141", "colour": "Black"},
        ])

        # Park the vehicle
        self.assertEqual(utils.park_vehicle('KA-01-HH-1235', 'White'), 2)
        # Test partial parking lot with new vehicle
        self.assertEqual(utils.parking_lot_status(), [
            {"slot_id": 1, "registration_number": "KA-01-HH-1234", "colour": "White"},
            {"slot_id": 2, "registration_number": "KA-01-HH-1235", "colour": "White"},
            {"slot_id": 3, "registration_number": "KA-01-BB-0001", "colour": "Black"},
            {"slot_id": 6, "registration_number": "KA-01-HH-3141", "colour": "Black"},
        ])

        # Complete the parking
        self.assertEqual(utils.park_vehicle('KA-01-HH-9999', 'White'), 4)
        self.assertEqual(utils.park_vehicle('KA-01-HH-7777', 'Red'), 5)
        # Test full parking lot
        self.assertEqual(utils.parking_lot_status(), [
            {"slot_id": 1, "registration_number": "KA-01-HH-1234", "colour": "White"},
            {"slot_id": 2, "registration_number": "KA-01-HH-1235", "colour": "White"},
            {"slot_id": 3, "registration_number": "KA-01-BB-0001", "colour": "Black"},
            {"slot_id": 4, "registration_number": "KA-01-HH-9999", "colour": "White"},
            {"slot_id": 5, "registration_number": "KA-01-HH-7777", "colour": "Red"},
            {"slot_id": 6, "registration_number": "KA-01-HH-3141", "colour": "Black"},
        ])

    def test_registration_numbers_for_cars_with_colour(self):
        # Call test_park_vehicle to re-use code
        self.test_park_vehicle()

        # Test for white
        self.assertEqual(utils.info_for_vehicles_with_colour("White", "registration_number"), ["KA-01-HH-1234", "KA-01-HH-9999"])  # White
        self.assertEqual(utils.info_for_vehicles_with_colour("white", "registration_number"), ["KA-01-HH-1234", "KA-01-HH-9999"])  # white

        # Unpark 4, 2, and 5
        self.assertTrue(utils.unpark_vehicle(4))
        self.assertTrue(utils.unpark_vehicle(2))
        self.assertTrue(utils.unpark_vehicle(5))
        # Park one vehicle
        self.assertEqual(utils.park_vehicle('KA-01-HH-1235', 'white'), 2)  # white

        # Test change in white
        self.assertEqual(utils.info_for_vehicles_with_colour("White", "registration_number"), ["KA-01-HH-1234", "KA-01-HH-1235"])  # White

    def test_slot_numbers_for_cars_with_colour(self):
        # Call test_park_vehicle to re-use code
        self.test_park_vehicle()

        # Test for white
        self.assertEqual(utils.info_for_vehicles_with_colour("White", "slot_id"), [1, 2])  # White
        self.assertEqual(utils.info_for_vehicles_with_colour("white", "slot_id"), [1, 2])  # white

        # Unpark 4, 2, and 5
        self.assertTrue(utils.unpark_vehicle(4))
        self.assertTrue(utils.unpark_vehicle(2))
        self.assertTrue(utils.unpark_vehicle(5))
        # Park some vehicles
        self.assertEqual(utils.park_vehicle('KA-01-HH-7777', 'Red'), 2)
        self.assertEqual(utils.park_vehicle('KA-01-HH-1235', 'white'), 4)  # white

        # Test change in white
        self.assertEqual(utils.info_for_vehicles_with_colour("White", "slot_id"), [1, 4])  # White

    def test_slot_number_for_registration_number(self):
        # Call test_park_vehicle to re-use code
        self.test_park_vehicle()

        # Test for KA-01-HH-9999
        self.assertEqual(utils.slot_number_for_registration_number("KA-01-HH-9999"), 2)
        # Test for KA-01-HH-7777
        self.assertEqual(utils.slot_number_for_registration_number("KA-01-HH-7777"), 4)

        # Unpark 4, 2, and 5
        self.assertTrue(utils.unpark_vehicle(4))
        self.assertTrue(utils.unpark_vehicle(2))
        self.assertTrue(utils.unpark_vehicle(5))
        # Park one vehicle
        self.assertEqual(utils.park_vehicle('KA-01-HH-1235', 'White'), 2)
        # Test for KA-01-HH-1235
        self.assertEqual(utils.slot_number_for_registration_number("KA-01-HH-1235"), 2)

    def test_slot_number_for_registration_number_not_found(self):
        # Call test_park_vehicle to re-use code
        self.test_park_vehicle()

        # Test for KA-01-HH-9990
        self.assertEqual(utils.slot_number_for_registration_number("KA-01-HH-9990"), -1)

        # But, test for KA-01-HH-9999
        self.assertEqual(utils.slot_number_for_registration_number("KA-01-HH-9999"), 2)

    def test_process_command_input(self):
        input_output = [
            ['create_parking_lot 6', 'Created a parking lot with 6 slots'],
            ['park KA-01-HH-1234 White', 'Allocated slot number: 1'],
            ['park KA-01-HH-9999 White', 'Allocated slot number: 2'],
            ['park KA-01-BB-0001 Black', 'Allocated slot number: 3'],
            ['park KA-01-HH-7777 Red', 'Allocated slot number: 4'],
            ['park KA-01-HH-2701 Blue', 'Allocated slot number: 5'],
            ['park KA-01-HH-3141 Black', 'Allocated slot number: 6'],
            ['leave 4', 'Slot number 4 is free'],
            ['status', 'Slot No.    Registration No    Colour\n1           KA-01-HH-1234      White\n2           KA-01-HH-9999      White\n3           KA-01-BB-0001      Black\n5           KA-01-HH-2701      Blue\n6           KA-01-HH-3141      Black'],
            ['park KA-01-P-333 White', 'Allocated slot number: 4'],
            ['park DL-12-AA-9999 White', 'Sorry, parking lot is full'],
            ['registration_numbers_for_cars_with_colour White', 'KA-01-HH-1234, KA-01-HH-9999, KA-01-P-333'],
            ['slot_numbers_for_cars_with_colour White', '1, 2, 4'],
            ['slot_number_for_registration_number KA-01-HH-3141', '6'],
            ['slot_number_for_registration_number MH-04-AY-1111', 'Not found']
        ]

        for input_string, output_string in input_output:
            self.assertEqual(utils.process_command_input(input_string), output_string)

        self.assertEqual(utils.process_command_input('exit'), 0)
        self.assertEqual(utils.process_command_input(''), 0)

    def test_process_command_input_file(self):
        output = [
            'Created a parking lot with 6 slots',
            'Allocated slot number: 1',
            'Allocated slot number: 2',
            'Allocated slot number: 3',
            'Allocated slot number: 4',
            'Allocated slot number: 5',
            'Allocated slot number: 6',
            'Slot number 4 is free',
            'Slot No.    Registration No    Colour\n1           KA-01-HH-1234      White\n2           KA-01-HH-9999      White\n3           KA-01-BB-0001      Black\n5           KA-01-HH-2701      Blue\n6           KA-01-HH-3141      Black',
            'Allocated slot number: 4',
            'Sorry, parking lot is full',
            'KA-01-HH-1234, KA-01-HH-9999, KA-01-P-333',
            '1, 2, 4',
            '6',
            'Not found'
        ]
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../fixtures/file_input.txt'), 'rU') as input_file:
            output_index = 0
            for command_input in input_file:
                command_input = command_input.rstrip('\n').rstrip()
                self.assertEqual(utils.process_command_input(command_input), output[output_index])
                output_index += 1
