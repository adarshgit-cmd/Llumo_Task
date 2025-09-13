from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet
from .auth_views import UserRegistrationView, UserProfileView

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', UserRegistrationView.as_view(), name='user_register'),
    path('auth/profile/', UserProfileView.as_view(), name='user_profile'),
]
