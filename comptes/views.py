from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import (RegisterSerializer,UserSerializer,ChangePasswordSerializer)

# creer un compte
class RegisterView(generics.CreateAPIView):

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class ProfileView(generics.RetrieveAPIView):

    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
# changer le mot de passe a la premiere connexion

class ChangePasswordView(APIView):

    def post(self, request):

        serializer = ChangePasswordSerializer(
            data=request.data
        )

        if serializer.is_valid():

            user = request.user

            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            if not user.check_password(old_password):

                return Response(
                    {
                        'error': 'Ancien mot de passe incorrect'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(new_password)

            user.must_change_password = False

            user.save()

            return Response(
                {
                    'message': 'Mot de passe modifié avec succès'
                }
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .services import*
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

from .models import DemandeAdmin, User
from .serializers import DemandeAdminSerializer
from .permissions import IsSuperAdmin

# creer un admin
class CreerDemandeAdminView(generics.CreateAPIView):

    queryset = DemandeAdmin.objects.all()

    serializer_class = DemandeAdminSerializer

    permission_classes = []

#voir la liste des demande
class ListeDemandesAdminView(generics.ListAPIView):

   queryset = DemandeAdmin.objects.filter(statut='en_attente')

   serializer_class = DemandeAdminSerializer

   permission_classes = [IsSuperAdmin]

# valider une demamde
class ValiderDemandeAdminView(APIView):

    permission_classes = [IsSuperAdmin]

    def post(self, request, pk):

        demande = DemandeAdmin.objects.get(id=pk)

        password = generate_password()

        utilisateur = User.objects.create_user(
            username=demande.nom,
            email=demande.email,
            password=password,
            role='admin',
            telephone=demande.telephone,
            cni=demande.cni
        )

        demande.statut = 'acceptee'
        demande.save()

        send_mail(
            subject='Compte administrateur Votify',
            message=f'''
Bonjour {demande.nom},

Votre demande administrateur a été acceptée sur l'app votify.
vous pouvez desormais creer et gerer vos scrutins.

Email : {demande.email}

Mot de passe : {password}

Veuillez modifier votre mot de passe après connexion.
''',
            from_email='laetitiamaelle740@gmail.com',
            recipient_list=[demande.email],
            fail_silently=False
        )

        return Response({
            'message': 'Compte administrateur créé avec succès'
        })
    

# refuser demande 

class RefuserDemandeAdminView(APIView):

    permission_classes = [IsSuperAdmin]

    def post(self, request, pk):

        demande = DemandeAdmin.objects.get(id=pk)

        demande.statut = 'refusee'
        demande.save()

        send_mail(
            subject='Demande administrateur refusée',
            message=f'''
Bonjour {demande.nom},

Votre demande d'accès administrateur à Votify
a été refusée.

Vous pouvez contacter le support
pour plus d'informations au 693823659.

Votify.
''',
            from_email='laetitiamaelle740@gmail.com',
            recipient_list=[demande.email],
            fail_silently=False
        )

        return Response({
            'message': 'Demande refusée'
        })
    
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# creer un admin directement 
# Vue pour la création directe d'un administrateur par le SuperAdmin
class CreerAdminDirectView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request):
        nom = request.data.get('username')
        email = request.data.get('email')
        telephone = request.data.get('telephone')
        cni = request.data.get('cni')

        if not nom or not email:
            return Response(
                {'error': 'Le nom d’utilisateur et l’email sont obligatoires'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Un utilisateur avec cet email existe déjà'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        password = generate_password()

        utilisateur = User.objects.create_user(
            username=nom,
            email=email,
            password=password,
            role='admin',
            telephone=telephone,
            cni=cni,
            must_change_password=True
        )

        # Envoi de l'email avec les accès
        send_mail(
            subject='Votre compte Administrateur Votify',
            message=f'''Bonjour {nom},

Un compte administrateur a été créé pour vous par le Super Administrateur sur l'application Votify.

Vos paramètres de connexion :
Email : {email}
Mot de passe temporaire : {password}

Veuillez modifier votre mot de passe dès votre première connexion.
''',
            from_email='laetitiamaelle740@gmail.com',
            recipient_list=[email],
            fail_silently=False
        )

        return Response({
            'message': 'Compte administrateur créé avec succès',
            'user': {
                'id': utilisateur.id,
                'username': utilisateur.username,
                'email': utilisateur.email,
                'role': utilisateur.role
            }
        }, status=status.HTTP_201_CREATED)
    
    # Voir la liste de tous les comptes administrateurs créés
class ListeAdministrateursView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        # On filtre la table User pour ne retourner que les comptes avec le rôle admin
        return User.objects.filter(role='admin')
    
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def toggle_statut_admin(request, pk):
    try:
        # On récupère l'admin
        administrateur = User.objects.get(pk=pk, role='admin')
    except User.DoesNotExist:
        return Response({"error": "Administrateur non trouvé"}, status=status.HTTP_404_NOT_FOUND)

    # Inversion pure et simple du statut actuel
    administrateur.is_active = not administrateur.is_active
    administrateur.save()

    return Response({
        "message": "Statut mis à jour avec succès",
        "is_active": administrateur.is_active  # On renvoie le nouvel état réel
    }, status=status.HTTP_200_OK)

# Ajouter cette vue dans comptes/views.py
# Elle permet à l'utilisateur connecté de modifier son username et telephone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer


class ModifierProfilView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        username  = request.data.get('username')
        telephone = request.data.get('telephone')

        if username:
            user.username = username
        if telephone is not None:
            user.telephone = telephone

        user.save()
        return Response({
            'message': 'Profil mis à jour',
            'username':  user.username,
            'telephone': user.telephone,
        })
# statistique

# À ajouter dans comptes/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from .permissions import IsSuperAdmin
from .models import User
from .models import DemandeAdmin

# Import des modèles des autres apps
# (adapter les chemins selon votre projet)
try:
    from scrutins.models import Scrutin
except ImportError:
    Scrutin = None

try:
    from vote.models import InscriptionScrutin
except ImportError:
    InscriptionScrutin = None


class StatsSuperAdminView(APIView):
    """
    Retourne les statistiques globales pour le dashboard SuperAdmin.
    GET /api/auth/superadmin/stats/
    """
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        # Nombre total de scrutins
        total_scrutins = Scrutin.objects.count() if Scrutin else 0

        # Nombre total d'admins actifs
        total_admins = User.objects.filter(role='admin').count()

        # Nombre total d'électeurs
        total_electeurs = User.objects.filter(role='electeur').count()

        # Demandes en attente
        demandes_attente = DemandeAdmin.objects.filter(statut='en_attente').count()

        return Response({
            'total_scrutins':   total_scrutins,
            'total_admins':     total_admins,
            'total_electeurs':  total_electeurs,
            'demandes_attente': demandes_attente,
        })
