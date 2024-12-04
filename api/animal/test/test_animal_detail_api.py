from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status
from animal.models import Animal, AnimalDetail
from animal.serializers import AnimalDetailSerializer


def details_url(animal_id):
    return reverse('animal:animaldetail-list', args=[animal_id])

def detail_details_url(animal_id, id):
    return reverse('animal:animaldetail-detail', args=[animal_id, id])

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

def create_detail(animal, **params):
    defaults = {
        'name':'Default Detail',
        'value':'Test Value',
        'description':'Default Description',
        'date_recorded':'2024-01-01'     
    }
    defaults.update(params)
    detail = AnimalDetail.objects.create(animal=animal, **defaults)
    return detail

class PublicTestDetailApi(TestCase):
    """Test for error thrown for unauthenticated users"""
    def setUp(self) -> None:
        self.client = APIClient()

    def test_get_details(self):
        """Test for error thrown with unauthenticated user """
        user = create_user()
        animal = create_animal(user=user)
        url = details_url(animal.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_detail_throws_error(self):
        """Test for error thrown with unauthenticated user creates vaccine """
        user = create_user()
        animal = create_animal(user=user)
        url = details_url(animal.id)
        payload = {
            'name':'Default Detail',
            'value':'Test Value',
            'description':'Default Description',
            'date_recorded':'2024-01-01',              
        }
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_delete_detail(self):
        """Test deleting a detail by an unauthenticated user"""
        user = create_user()
        animal = create_animal(user=user)
        detail = create_detail(animal)
        url = detail_details_url(animal_id=animal.id, id=detail.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        

class PrivateTestMeasurementApi(TestCase):
    """Test for authenticated users"""
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user(email="test4@example.com")
        self.client.force_authenticate(self.user)

    def test_get_details(self):
        """Test for retrieve with authenticated user """
        animal = create_animal(user=self.user)
        create_detail(animal)
        create_detail(animal, name="New Detail")
        url = details_url(animal.id)
        res = self.client.get(url)
        details = AnimalDetail.objects.filter(animal=animal).order_by('name','date_recorded')   
        self.assertEqual(res.status_code, status.HTTP_200_OK)        
        self.assertEqual(res.data[0]['name'], details[0].name)
        
    def test_get_other_users_animal_details(self):
        """Test for error when attempting to retrieve dtails of an animal of another user"""
        user = create_user(email='test5@example.com')
        animal = create_animal(user=user)
        create_detail(animal)
        url = details_url(animal.id)
        res = self.client.get(url)
        
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_create_details_for_animal(self):
        """Test creating a details for an animal"""
        animal = create_animal(user=self.user)
        url = details_url(animal.id)
        payload = {
            'name': 'TEst',
            'value': "5",
            'date_recorded': "2024-01-01"           
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        animal.refresh_from_db
        details = animal.details.filter(name=payload['name'])
        self.assertEqual(res.data['name'], details[0].name)

    def test_create_detail_for_other_users_animal(self):
        """Test creating a dtail for an animal that belongs to another user"""
        user=create_user(email='Test5@example.com')
        animal = create_animal(user=user)
        url = details_url(animal.id)
        payload = {
            'name': 'TEst',
            'value': "5",
            'date_recorded': "2024-01-01"           
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_detail(self):
        """Update detail information"""
        animal = create_animal(user=self.user)
        detail = create_detail(animal)
        payload = {
            'name': 'TEst',
            'value': "5",
            'date_recorded': "2024-01-01"           
        }
        url = detail_details_url(animal_id=animal.id, id=detail.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        detail.refresh_from_db()
        self.assertEqual(detail.name, payload['name'])

    def test_update_other_user_animal_measurement(self):
        """Update detail information for another user's animal"""
        user = create_user('Test5@example.com')
        animal = create_animal(user=user)        
        detail = create_detail(animal=animal, name="Test5")
        payload = {
            'name': 'TEst',
            'value': "5",
            'date_recorded': "2024-01-01"           
        }
        url = detail_details_url(animal_id=animal.id, id=detail.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        detail.refresh_from_db()
        self.assertEqual(detail.name, "Test5")

    def test_delete_detail(self):
        """Test deleting a detail that belongs to an animal the user created"""
        animal = create_animal(user=self.user)
        detail = create_detail(animal)
        url = detail_details_url(animal_id=animal.id, id=detail.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_other_user_measurement(self):
        """Test deleting a measurement that belongs to an animal the user created"""
        user = create_user('Test5@example.com')
        animal = create_animal(user=user)
        detail = create_detail(animal)
        url = detail_details_url(animal_id=animal.id, id=detail.id)       
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        
