from django.urls import path
from .views import CreateUserAPIView, CreateTokenAPIView

app_name = 'user'


urlpatterns = [
    path('create/', CreateUserAPIView.as_view(),
         name='create'),
    path('token/', CreateTokenAPIView.as_view(),
         name='token')
]
