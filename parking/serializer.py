from rest_framework import serializers
from parking.models import ParkingModels


class ParkingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingModels
        fields = ["id", "plate", "paid", "arrival_time", "departure_time"]
        extra_kwargs = {'paid': {'read_only': True},
                        'arrival_time': {'read_only': True},
                        'departure_time': {'read_only': True}}
    
    def validate(self, attrs):
        # This is necessary to force the validation of the ParkingModel (clean),
        # since the restframework doesn't do this automatically.
        instance = ParkingModels(**attrs)
        instance.clean()
        return attrs