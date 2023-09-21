from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path("about-me/", views.about_me, name='about-me'),
    path("works/", views.works, name='works'),
    path("send-mail/", views.contact_form, name='contact-form'),
]
