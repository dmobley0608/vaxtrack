from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'animals', views.AnimalViewSet)
router.register(r'measurements', views.AnimalMeasurementViewSet)
# router.register(r'vaccinations', views.VaccinationViewSet)
router.register(r'details', views.AnimalDetailViewSet)

vaccine_router = DefaultRouter()
vaccine_router.register(r'vaccinations', views.VaccinationViewSet)
app_name = 'animal'

urlpatterns = [
    path('', include(router.urls)),
    path('<int:animal_id>/', include(vaccine_router.urls))
]
