from django.urls import path, include

urlpatterns = [
    path('', include('POS_APP.urls')),  # <- Include accounts app URLs here
]