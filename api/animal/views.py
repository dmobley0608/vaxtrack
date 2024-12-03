from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Animal, AnimalMeasurement, Vaccination, AnimalDetail
from .serializers import AnimalSerializer, AnimalMeasurementSerializer, VaccinationSerializer, AnimalDetailSerializer
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

class AnimalViewSet(viewsets.ModelViewSet):
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(owner=user.id).order_by('name')


class AnimalMeasurementViewSet(viewsets.ModelViewSet):
    queryset = AnimalMeasurement.objects.all()
    serializer_class = AnimalMeasurementSerializer

class VaccinationViewSet(viewsets.ModelViewSet):
    queryset = Vaccination.objects.all()
    serializer_class = VaccinationSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            animal = get_object_or_404(Animal, id = self.kwargs['animal_id'])
            if animal.owner == user:
                return self.queryset.filter(animal=animal).order_by('-date_administered')
            else:
                raise PermissionDenied('You are not allowed to access this animal.')
        else:
            raise PermissionDenied("You must be logged in to utilize this feature.")

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_authenticated:
            animal = get_object_or_404(Animal, id = self.kwargs['animal_id'])
            if animal.owner == user:
               serializer.save(animal=animal)
            else:
                raise PermissionDenied('You are not allowed to access this animal.')
        else:
            raise PermissionDenied("You must be logged in to utilize this feature.")

class AnimalDetailViewSet(viewsets.ModelViewSet):
    queryset = AnimalDetail.objects.all()
    serializer_class = AnimalDetailSerializer
