from pickle import FALSE
from django.core.exceptions import ValidationError
from django.test import TestCase
from parking.models import ParkingModels
import datetime

class ParkingModelTest(TestCase):
    def insert_plate(self, plate, arrival="2022-07-15 10:00:00", departure=None, paid=False):
        dt = ParkingModels(plate=plate, arrival_time=arrival, 
                            departure_time=departure, paid=paid)
        if dt.full_clean():
            dt.save()
        return dt

    def test_valid_insert_data(self):
        PLATE = "ABC-1234"
        ARRIVAL = "2022-07-15 10:00:00"
        parking = self.insert_plate(PLATE, ARRIVAL)
        self.assertIsNotNone(parking)
        self.assertEqual(parking.plate, PLATE)
        self.assertEqual(str(parking), PLATE)
        self.assertEqual(parking.arrival_time, datetime.datetime(2022, 7, 15, 10, 0))
        self.assertIsNone(parking.departure_time)

    def test_invalid_plate_insert_data(self):
        ERR_MSG = "Invalid plate, please use the format AAA-9999"
        invalid_plate_list = ["ABC_1234", "ABCD-1234", "ABC-12345", "AB-1234",
                                "ABC-123", "ABC1234"]
        for inv_plate in invalid_plate_list:
            with self.assertRaisesMessage(ValidationError, ERR_MSG):
                self.insert_plate(inv_plate)

    def test_invalid_departure_without_payment(self):
        ERR_MSG = "You cannot register the departure without confirming the payment"
        PLATE = "ABC-1234"
        ARRIVAL = "2022-07-15 10:00:00"
        DEPARTURE = "2022-07-15 12:00:00"
        PAID = False
        with self.assertRaisesMessage(ValidationError, ERR_MSG):
            self.insert_plate(plate=PLATE, arrival=ARRIVAL, departure=DEPARTURE, 
                                paid=PAID)

    def test_invalid_duplicated_plate_without_departure(self):
        ERR_MSG = "It is not possible to enter this data because the same " \
                    "plate is in a record without having been finalized."
        PLATE = "ABC-1234"
        ARRIVAL = "2022-07-15 10:00:00"
        ParkingModels.objects.create(plate=PLATE, arrival_time=ARRIVAL,
                                        departure_time=None, paid=False)
        with self.assertRaisesMessage(ValidationError, ERR_MSG):
            self.insert_plate(plate=PLATE, arrival=ARRIVAL, departure=None,
                                paid=False)

    def test_update_plate_without_departure(self):
        PLATE = "ABC-1234"
        ARRIVAL = "2022-07-15 10:00:00"
        dt = ParkingModels.objects.create(plate=PLATE, arrival_time=ARRIVAL,
                                            departure_time=None, paid=False)
        dt.arrival_time = datetime.datetime(2022, 7, 15, 11, 0)
        if dt.full_clean():
            dt.save()
        self.assertEqual(dt.arrival_time, datetime.datetime(2022, 7, 15, 11, 0))