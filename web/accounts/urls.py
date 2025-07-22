# urls.py
from allauth.account.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('accounts/logout/', LogoutView.as_view(), name='account_logout'),
]