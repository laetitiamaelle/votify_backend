from django.urls import path

from .views import *

urlpatterns = [
    path('creer/', CreerScrutinView.as_view()),
    path('mes-scrutins/', MesScrutinsView.as_view()),
    path('publics/', ListeScrutinsPublicsView.as_view()),
    path('detail/<int:pk>/', DetailScrutinView.as_view()),
    path('modifier/<int:pk>/', ModifierScrutinView.as_view()),
    path('supprimer/<int:pk>/', SupprimerScrutinView.as_view()),
    path('stats-dashboard/', StatsDashboardView.as_view()),
]