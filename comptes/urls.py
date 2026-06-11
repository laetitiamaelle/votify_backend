# comptes/urls.py — version finale avec route stats
from django.urls import path
from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    ProfileView,
    ChangePasswordView,
    ModifierProfilView,
    CreerDemandeAdminView,
    ListeDemandesAdminView,
    ValiderDemandeAdminView,
    RefuserDemandeAdminView,
    CreerAdminDirectView,
    ListeAdministrateursView,
    StatsSuperAdminView,    # <-- nouvelle vue à ajouter dans views.py
)
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/',               RegisterView.as_view()),
    path('login/',                  CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/',                TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/',                ProfileView.as_view()),
    path('modifier-profil/',        ModifierProfilView.as_view()),
    path('change-password/',        ChangePasswordView.as_view()),

    # Demandes admin
    path('demande-admin/',                      CreerDemandeAdminView.as_view()),
    path('liste-demandes-admin/',               ListeDemandesAdminView.as_view()),
    path('valider-demande-admin/<int:pk>/',      ValiderDemandeAdminView.as_view()),
    path('refuser-demande-admin/<int:pk>/',      RefuserDemandeAdminView.as_view()),

    # SuperAdmin
    path('superadmin/creer-admin/',             CreerAdminDirectView.as_view(), name='creer-admin-direct'),
    path('superadmin/admins/',                  ListeAdministrateursView.as_view(), name='liste-admins'),
    path('superadmin/admins/<int:pk>/statut/',  views.toggle_statut_admin, name='toggle-statut-admin'),
    path('superadmin/stats/',                   StatsSuperAdminView.as_view(), name='stats-superadmin'),  # <-- nouvelle
]
