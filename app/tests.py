import os
import unittest

from app import db, parking_lot, models, utils

class ParkingLotTests(unittest.TestCase):

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
        utils.create_parking_lot(self.total_slots)
        self.assertEqual(models.Slot.query.count(), self.total_slots)

        # TODO: Test repeat call

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

