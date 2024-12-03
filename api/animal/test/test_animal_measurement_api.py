from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status
from animal.models import Animal, AnimalMeasurement


def measuremnt_url(animal_id):
    return reverse('animal:animalmeasurement-list', args=[animal_id])

def measurement_details_url(animal_id, id):
    return reverse('animal:animalmeasurement-detail', args=[animal_id, id])

def create_user(email='test@example.com', password='test123456'):
    return get_user_model().objects.create_user(email, password)

def create_animal(user, **params):
    """"Creates and returns an animal"""
    defaults = {
            'name': 'Test Animal',
            'species': 'Test Species',
            'breed': 'Test Breed',
            'date_of_birth': '2024-01-01'
        }
    defaults.update(params)
    animal = Animal.objects.create(owner=user, **defaults)
    return animal


class PublicTestMeasurementApi(TestCase):
    """Test for error thrown for unauthenticated users"""
    def setUp(self) -> None:
        self.client = APIClient()

    def test_get_measurements(self):
        """Test for error thrown with unauthenticated user """
        user = create_user()
        animal = create_animal(user=user)
        url = measuremnt_url(animal.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_measurement_throws_error(self):
        """Test for error thrown with unauthenticated user creates vaccine """
        user = create_user()
        animal = create_animal(user=user)
        url = measuremnt_url(animal.id)
        payload = {
            'date': '2024-01-01',
            'weight': Decimal('808.25'),
            'height': Decimal('15.2')           
        }
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTestMeasurementApi(TestCase):
    """Test for authenticated users"""
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user(email="test4@example.com")
        self.client.force_authenticate(self.user)

    def test_get_measurements(self):
        """Test for retrieve with authenticated user """
        animal = create_animal(user=self.user)
        url = measuremnt_url(animal.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_unowned_animal_measurements(self):
        """Test for retrieve another user's animal measurements with authenticated user """
        user = create_user()
        animal = create_animal(user=user)
        url = measuremnt_url(animal.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_measurement_for_animal(self):
        """Test creating a measurement for an animal"""
        animal = create_animal(user=self.user)
        url = measuremnt_url(animal.id)
        payload = {
            'date': '2024-01-01',
            'weight': Decimal('808.25'),
            'height': Decimal('15.2')           
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        animal.refresh_from_db
        measurement = animal.measurements.filter(weight=payload['weight'])
        self.assertEqual(Decimal(res.data['weight']), measurement[0].weight)

    def test_create_measurement_for_other_users_animal(self):
        """Test creating a measurement for an animal that belongs to another user"""
        user=create_user(email='Test5@example.com')
        animal = create_animal(user=user)
        url = measuremnt_url(animal.id)
        payload = {
            'date': '2024-01-01',
            'weight': Decimal('808.25'),
            'height': Decimal('15.2')           
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_measurement(self):
        """Update measurment information"""
        animal = create_animal(user=self.user)
        measurement = AnimalMeasurement.objects.create(
           date= '2024-01-01',
            weight= Decimal('808.25'),
            height= Decimal('15.2'),
            animal=animal
        )
        payload = {
            'date': '2024-01-01',
            'weight': Decimal('0.00'),
            'height': Decimal('15.2')           
        }
        url = measurement_details_url(animal_id=animal.id, id=measurement.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        measurement.refresh_from_db()
        self.assertEqual(measurement.weight, payload['weight'])

    def test_update_other_user_animal_measurement(self):
        """Update measurement information for another user's animal"""
        user = create_user('Test5@example.com')
        animal = create_animal(user=user)
        measurement = AnimalMeasurement.objects.create(
            date= '2024-01-01',
            weight= Decimal('808.25'),
            height= Decimal('15.2'),
            animal=animal
        )
        payload = {
            'date': '2024-01-01',
            'weight': Decimal('800'),
            'height': Decimal('15.2')           
        }
        url = measurement_details_url(animal_id=animal.id, id=measurement.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        measurement.refresh_from_db()
        self.assertEqual(measurement.weight, Decimal('808.25'))

    def test_delete_measurement(self):
        """Test deleting a measurement that belongs to an animal the user created"""
        animal = create_animal(user=self.user)
        measurement = AnimalMeasurement.objects.create(
             date= '2024-01-01',
            weight= Decimal('808.25'),
            height= Decimal('15.2'),
            animal=animal
        )
        url = measurement_details_url(animal_id=animal.id, id=measurement.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_other_user_measurement(self):
        """Test deleting a measurement that belongs to an animal the user created"""
        user = create_user('Test5@example.com')
        animal = create_animal(user=user)
        measurement = AnimalMeasurement.objects.create(
            date= '2024-01-01',
            weight= Decimal('808.25'),
            height= Decimal('15.2'),
            animal=animal
        )
        url = measurement_details_url(animal_id=animal.id, id=measurement.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        