from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from parking.models import ParkingModels
import datetime
from freezegun import freeze_time

ERR_MSG_DUPLICATED = "It is not possible to enter this data because the same " \
            "plate is in a record without having been finalized."
ERR_MSG_NO_PAYMENT = "You cannot register the departure without confirming the payment"
ERR_MSG_INVALID_FORMAT = "Invalid plate, please use the format AAA-9999"

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
        invalid_plate_list = ["ABC_1234", "ABCD-1234", "ABC-12345", "AB-1234",
                                "ABC-123", "ABC1234"]
        for inv_plate in invalid_plate_list:
            with self.assertRaisesMessage(ValidationError, ERR_MSG_INVALID_FORMAT):
                self.insert_plate(inv_plate)

    def test_invalid_departure_without_payment(self):
        PLATE = "ABC-1234"
        ARRIVAL = "2022-07-15 10:00:00"
        DEPARTURE = "2022-07-15 12:00:00"
        PAID = False
        with self.assertRaisesMessage(ValidationError, ERR_MSG_NO_PAYMENT):
            self.insert_plate(plate=PLATE, arrival=ARRIVAL, departure=DEPARTURE, 
                                paid=PAID)

    def test_invalid_duplicated_plate_without_departure(self):
        PLATE = "ABC-1234"
        ARRIVAL = "2022-07-15 10:00:00"
        ParkingModels.objects.create(plate=PLATE, arrival_time=ARRIVAL,
                                        departure_time=None, paid=False)
        with self.assertRaisesMessage(ValidationError, ERR_MSG_DUPLICATED):
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

class ParkingViewSetTest(APITestCase):
    url = "/api/v1/parking/"

    def test_add_car(self):
        PLATE = "ABC-1234"
        ret = self.client.post(self.url, {"plate": PLATE}, format="json")
        self.assertEqual(ret.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ret.data["plate"], PLATE)

    def test_invalid_add_car(self):
        PLATE = "123-ABCD"
        ret = self.client.post(self.url, {"plate": PLATE}, format="json")
        self.assertEqual(ret.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaisesMessage(ret.data, ERR_MSG_INVALID_FORMAT)

    def test_invalid_duplicated_no_finished(self):
        PLATE = "ABC-1234"
        ret = self.client.post(self.url, {"plate": PLATE}, format="json")
        self.assertEqual(ret.status_code, status.HTTP_201_CREATED)
        ret = self.client.post(self.url, {"plate": PLATE}, format="json")
        self.assertEqual(ret.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaisesMessage(ret.data, ERR_MSG_DUPLICATED)

    def test_pay(self):
        url_pay = "/api/v1/parking/{}/pay/"
        PLATE = "ABC-1234"
        ret = self.client.post(self.url, {"plate": PLATE}, format="json")
        self.assertEqual(ret.status_code, status.HTTP_201_CREATED)
        self.assertFalse(ret.data["paid"])
        id = ret.data["id"]

        ret_put = self.client.put(url_pay.format(id), format="json")
        self.assertEqual(ret_put.status_code, status.HTTP_202_ACCEPTED)
        dt = ParkingModels.objects.get(id=id)
        self.assertTrue(dt.paid)

    def test_out(self):
        url_out = "/api/v1/parking/{}/out/"
        PLATE = "ABC-1234"
        parking = ParkingModels.objects.create(plate=PLATE, paid=True)
        self.assertIsNone(parking.departure_time)

        ret_out = self.client.put(url_out.format(parking.id), format="json")
        self.assertEqual(ret_out.status_code, status.HTTP_202_ACCEPTED)
        dt = ParkingModels.objects.get(id=parking.id)
        self.assertIsNotNone(dt.departure_time)

    def test_invalid_out_without_payment(self):
        url_out = "/api/v1/parking/{}/out/"
        PLATE = "ABC-1234"
        parking = ParkingModels.objects.create(plate=PLATE, paid=False)
        self.assertIsNone(parking.departure_time)

        ret_out = self.client.put(url_out.format(parking.id), format="json")
        self.assertEqual(ret_out.status_code, status.HTTP_400_BAD_REQUEST)
        dt = ParkingModels.objects.get(id=parking.id)
        self.assertIsNone(dt.departure_time)

    @freeze_time("2022-07-15 10:00:00")
    def test_search_by_plate(self):
        url = "/api/v1/parking/{}/"
        PLATE = "ABC-1234"
        DT_OUT = "2022-07-15 10:20:00"
        ParkingModels.objects.create(plate=PLATE, paid=True, departure_time=DT_OUT)

        ret = self.client.get(url.format(PLATE), format="json")
        self.assertEqual(ret.status_code, status.HTTP_200_OK)
        self.assertEqual(ret.data[0]["time"], "20 minutes")
        self.assertTrue(ret.data[0]["left"])

    def test_search_by_plate_with_no_departure(self):
        url = "/api/v1/parking/{}/"
        PLATE = "ABC-1234"

        with freeze_time("2022-07-15 12:00:00"):
            ParkingModels.objects.create(plate=PLATE)

        with freeze_time("2022-07-15 12:01:00"): # 1 minute
            ret = self.client.get(url.format(PLATE), format="json")
            self.assertEqual(ret.status_code, status.HTTP_200_OK)
            self.assertEqual(ret.data[0]["time"], "1 minute")
            self.assertFalse(ret.data[0]["left"])

    def test_invalid_notfound_search(self):
        url = "/api/v1/parking/{}/"
        PLATE = "ABC-1234"
        NOTFOUND_PLATE = "ZZZ-9999"
        ParkingModels.objects.create(plate=PLATE)

        ret = self.client.get(url.format(NOTFOUND_PLATE), format="json")
        self.assertEqual(ret.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_plate_format_search(self):
        url = "/api/v1/parking/{}/"
        PLATE = "ABC-1234"
        invalid_plate_list = ["ABC_1234", "ABCD-1234", "ABC-12345", "AB-1234",
                                "ABC-123", "ABC1234"]
        ParkingModels.objects.create(plate=PLATE, paid=True)

        for invplate in invalid_plate_list:
            ret = self.client.get(url.format(invplate), format="json")
            self.assertEqual(ret.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

