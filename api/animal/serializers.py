from rest_framework import serializers
from .models import Animal, AnimalMeasurement, Vaccination, AnimalDetail





class AnimalMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalMeasurement
        fields = ['date', 'weight', 'height']

class VaccinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaccination
        fields = ['vaccine_name', 'date_administered', 'description', 'next_due_date']

class AnimalDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalDetail
        fields = '__all__'

class AnimalSerializer(serializers.ModelSerializer):
    details = AnimalDetailSerializer(many=True, required=False)
    vaccinations = VaccinationSerializer(many=True, required=False)
    measurements = AnimalMeasurementSerializer(many=True, required=False)
    class Meta:
        model = Animal
        fields = ['name', 'date_of_birth', 'species', 'breed','measurements', 'details', 'vaccinations']
        read_only = ['id']

    def create(self, validated_data):
        user = self.context['request'].user
        animal = Animal.objects.create(owner=user, **validated_data)
        return animal




