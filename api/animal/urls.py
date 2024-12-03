from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'animals', views.AnimalViewSet)


sub_router = DefaultRouter()
sub_router.register(r'vaccinations', views.VaccinationViewSet)
sub_router.register(r'measurements', views.AnimalMeasurementViewSet)
sub_router.register(r'details', views.AnimalDetailViewSet)
app_name = 'animal'

urlpatterns = [
    path('', include(router.urls)),
    path('<int:animal_id>/', include(sub_router.urls))
]
