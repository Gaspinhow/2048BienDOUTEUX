from django.urls import path

from . import views

app_name = "catalogue"
urlpatterns = [
    path("", views.liste, name="liste"),
    path("categorie/<slug:categorie_slug>/", views.liste, name="categorie"),
    path("article/<slug:slug>/", views.detail, name="detail"),
]
