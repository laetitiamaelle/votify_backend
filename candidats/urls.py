from django.urls import path

from .views import *


urlpatterns = [

    path(
        'ajouter/',
        AjouterCandidatView.as_view()
    ),

    path(
        'scrutin/<int:scrutin_id>/',
        ListeCandidatsScrutinView.as_view()
    ),

    path(
        'modifier/<int:pk>/',
        ModifierCandidatView.as_view()
    ),

    path(
        'supprimer/<int:pk>/',
        SupprimerCandidatView.as_view()
    ),
]