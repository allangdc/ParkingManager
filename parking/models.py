from queue import Empty
from django.db import models
from django.db.models import Q
from  django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

ERR_PLATE_MSG = 'Invalid plate, please use the format AAA-9999'
ERR_DEPARTURE_NOT_PAID = "You cannot register the departure without confirming the payment"
ERR_DUPLICATED_NO_FINISHED = "It is not possible to enter this data because " \
                    "the same plate is in a record without having been finalized."

class ParkingModels(models.Model):
    plate = models.CharField(max_length=8, null=False, blank=False, validators=[
            RegexValidator(
                regex='^[A-Z]{3}-[0-9]{4}$',
                message=ERR_PLATE_MSG,
            ),
        ], db_index=True)
    paid = models.BooleanField(default=False)
    arrival_time = models.DateTimeField(auto_now_add=True)
    departure_time = models.DateTimeField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.plate

    def clean(self) -> None:
        errors = dict()
        if self.departure_time is not None and self.paid is False:
            errors["paid"] = ValidationError(ERR_DEPARTURE_NOT_PAID)
        dt = ParkingModels.objects.filter(~Q(id=self.id) & 
                                          Q(plate=self.plate) &
                                          Q(departure_time=None))
        if len(dt) > 0:
            errors["plate"] = ValidationError(ERR_DUPLICATED_NO_FINISHED)
        if errors:
            raise ValidationError(errors)
        super().clean()