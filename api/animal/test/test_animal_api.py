from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from animal.models import Animal
from animal.serializers import AnimalSerializer


ANIMAL_URL = reverse('animal:animal-list')

def animal_detail_url(animal_id):
    return reverse('animal:animal-detail', args=[animal_id])

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


class PublicTestAnimalAPI(TestCase):
    """Test to ensure unauthorized user can't access or create animals"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_public_request_returns_error(self):
        """Test to ensure unauthenticated request return error"""
        res = self.client.get(ANIMAL_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTestAnimalAPI(TestCase):
    """Test authenticated requests to animal api"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_fetch_animals(self):
        """Test that only animals created by user are returned"""
        create_animal(user=self.user)
        create_animal(user=self.user, name="Test2")
        user = create_user(email='test2@example.com')
        create_animal(user)

        res = self.client.get(ANIMAL_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        animals = Animal.objects.filter(owner=self.user)
        self.assertEqual(animals.count(), 2)

    def test_get_animal_detail(self):
        """Test for fetching animal details"""
        animal = create_animal(user=self.user)
        url = animal_detail_url(animal.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], animal.name)

    def test_create_animal(self):
        """Test for successful creation of animal"""
        payload = {
            'name': 'Test Animal',
            'species': 'Test Species',
            'breed': 'Test Breed',
            'date_of_birth': '2024-01-01'
        }

        res = self.client.post(ANIMAL_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_animal(self):
        """Test updating animal"""
        animal = create_animal(user=self.user)
        payload={
            'name':'Updated name'
        }
        url = animal_detail_url(animal.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        animal.refresh_from_db()
        self.assertEqual(res.data['name'], payload['name'])

    def test_update_animal_produces_error(self):
        """Updating an animal belonging to another user produces error"""
        user = create_user(email='newuser@example.com')
        animal = create_animal(user=user)
        payload={
            'name':'Updated name'
        }
        url = animal_detail_url(animal.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        animal.refresh_from_db()
        self.assertNotEqual(animal.name, payload['name'])


    def test_deleting_animal(self):
        """test deleting an animal"""
        animal = create_animal(user=self.user)
        url = animal_detail_url(animal.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_deleting_other_user_animal(self):
        """test deleting another user's animal produces error"""
        user = create_user(email='anotheruser@example.com')
        animal = create_animal(user=user)
        url = animal_detail_url(animal.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        exists = Animal.objects.filter(id=animal.id, owner=user).exists()
        self.assertTrue(exists)



