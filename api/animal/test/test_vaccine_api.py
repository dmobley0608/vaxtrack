from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from animal.models import Animal, Vaccination


def vaccine_url(animal_id):
    return reverse('animal:vaccination-list', args=[animal_id])

def vaccine_details_url(animal_id, id):
    return reverse('animal:vaccination-detail', args=[animal_id, id])

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


class PublicTestVaccinationApi(TestCase):
    """Test for error thrown for unauthenticated users"""
    def setUp(self) -> None:
        self.client = APIClient()

    def test_get_vaccinations(self):
        """Test for error thrown with unauthenticated user """
        user = create_user()
        animal = create_animal(user=user)
        url = vaccine_url(animal.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_vaccinations(self):
        """Test for error thrown with unauthenticated user creates vaccine """
        user = create_user()
        animal = create_animal(user=user)
        url = vaccine_url(animal.id)
        payload = {
            'vaccine_name': 'Rabies',
            'date_administered': '2024-01-01',
            'description': 'Rabies Shot'
        }
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTestVaccinationApi(TestCase):
    """Test for authenticated users"""
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user(email="test4@example.com")
        self.client.force_authenticate(self.user)

    def test_get_vaccinations(self):
        """Test for retrieve with authenticated user """
        animal = create_animal(user=self.user)
        url = vaccine_url(animal.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_unowned_animal_vaccinations(self):
        """Test for retrieve another user's animal vaccinations with authenticated user """
        user = create_user()
        animal = create_animal(user=user)
        url = vaccine_url(animal.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_vaccine_for_animal(self):
        """Test creating a vaccine for an animal"""
        animal = create_animal(user=self.user)
        url = vaccine_url(animal.id)
        payload = {
            'vaccine_name': 'Rabies',
            'date_administered': '2024-01-01',
            'description': 'Rabies Shot',
            'next_due_date': '2025-01-01',
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        animal.refresh_from_db
        vaccine = animal.vaccinations.filter(vaccine_name=payload['vaccine_name'])
        self.assertEqual(res.data['vaccine_name'], vaccine[0].vaccine_name)

    def test_create_vaccine_for_other_users_animal(self):
        """Test creating a vaccine for an animal that belongs to another user"""
        user=create_user(email='Test5@example.com')
        animal = create_animal(user=user)
        url = vaccine_url(animal.id)
        payload = {
            'vaccine_name': 'Rabies',
            'date_administered': '2024-01-01',
            'description': 'Rabies Shot',
            'next_due_date': '2025-01-01',
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_vaccine(self):
        """Update vaccine information"""
        animal = create_animal(user=self.user)
        vaccine = Vaccination.objects.create(
            vaccine_name="Rabies",
            animal=animal,
            date_administered = '2024-01-01',
            next_due_date="2025-01-01"
        )
        payload = {
            'vaccine_name': 'Parvo',
            'date_administered': '2024-06-01',
            'description': 'Rabies Shot',
            'next_due_date': '2025-06-01',
        }
        url = vaccine_details_url(animal_id=animal.id, id=vaccine.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        vaccine.refresh_from_db()
        self.assertEqual(vaccine.vaccine_name, payload['vaccine_name'])

    def test_update_other_user_animal_vaccine(self):
        """Update vaccine information for another user's animal"""
        user = create_user('Test5@example.com')
        animal = create_animal(user=user)
        vaccine = Vaccination.objects.create(
            vaccine_name="Rabies",
            animal=animal,
            date_administered = '2024-01-01',
            next_due_date="2025-01-01"
        )
        payload = {
            'vaccine_name': 'Rabies',
            'date_administered': '2024-06-01',
            'description': 'Rabies Shot',
            'next_due_date': '2025-06-01',
        }
        url = vaccine_details_url(animal_id=animal.id, id=vaccine.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        vaccine.refresh_from_db()
        self.assertEqual(vaccine.vaccine_name, 'Rabies')

    def test_delete_vaccine(self):
        """Test deleting a vaccing that belongs to an animal the user created"""
        animal = create_animal(user=self.user)
        vaccine = Vaccination.objects.create(
            vaccine_name="Rabies",
            animal=animal,
            date_administered = '2024-01-01',
            next_due_date="2025-01-01"
        )
        url = vaccine_details_url(animal_id=animal.id, id=vaccine.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_other_user_vaccine(self):
        """Test deleting a vaccing that belongs to an animal the user created"""
        user = create_user('Test5@example.com')
        animal = create_animal(user=user)
        vaccine = Vaccination.objects.create(
            vaccine_name="Rabies",
            animal=animal,
            date_administered = '2024-01-01',
            next_due_date="2025-01-01"
        )
        url = vaccine_details_url(animal_id=animal.id, id=vaccine.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        