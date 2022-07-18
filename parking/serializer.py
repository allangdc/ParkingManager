from rest_framework import serializers
from parking.models import ParkingModels
import datetime


class ParkingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingModels
        fields = ["id", "plate", "paid"]
        extra_kwargs = {'paid': {'read_only': True}}
    
    def validate(self, attrs):
        # This is necessary to force the validation of the ParkingModel (clean),
        # since the restframework doesn't do this automatically.
        instance = ParkingModels(**attrs)
        instance.clean()
        return attrs

    def calc_time_parking(self, arrival, departure):
        if departure is None:
            date_ref = datetime.datetime.now()
        else:
            date_ref = departure
        duration = date_ref - arrival
        duration_min = round(duration.total_seconds() / 60)
        if duration_min != 1:
            return "{} minutes".format(duration_min)
        return "{} minute".format(duration_min)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['time'] = self.calc_time_parking(instance.arrival_time,
                                                        instance.departure_time)
        representation['left'] = instance.departure_time is not None
        return representation