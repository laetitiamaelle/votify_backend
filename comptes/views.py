from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.conf import settings
from django.contrib.auth import get_user_model
import resend

from .models import User, DemandeAdmin
from .serializers import (
    RegisterSerializer, UserSerializer,
    ChangePasswordSerializer, DemandeAdminSerializer,
    CustomTokenObtainPairSerializer
)
from .permissions import IsSuperAdmin
from .services import generate_password

try:
    from scrutins.models import Scrutin
except ImportError:
    Scrutin = None

ADMIN_EMAIL = 'wandjikamdemlaetitiamaelle@gmail.com'


def send_resend_email(subject, message):
    resend.api_key = settings.RESEND_API_KEY
    try:
        resend.Emails.send({
            'from': 'onboarding@resend.dev',
            'to': ADMIN_EMAIL,
            'subject': subject,
            'text': message
        })
    except Exception as e:
        print(f"Erreur envoi email : {e}")


# ── Compte électeur ───────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'error': 'Ancien mot de passe incorrect'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.validated_data['new_password'])
            user.must_change_password = False
            user.save()
            return Response({'message': 'Mot de passe modifié avec succès'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ModifierProfilView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        username = request.data.get('username')
        telephone = request.data.get('telephone')
        if username:
            user.username = username
        if telephone is not None:
            user.telephone = telephone
        user.save()
        return Response({
            'message': 'Profil mis à jour',
            'username': user.username,
            'telephone': user.telephone,
        })


# ── JWT ───────────────────────────────────────────────────

from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ── Demandes admin ────────────────────────────────────────

class CreerDemandeAdminView(generics.CreateAPIView):
    queryset = DemandeAdmin.objects.all()
    serializer_class = DemandeAdminSerializer
    permission_classes = []


class ListeDemandesAdminView(generics.ListAPIView):
    queryset = DemandeAdmin.objects.filter(statut='en_attente')
    serializer_class = DemandeAdminSerializer
    permission_classes = [IsSuperAdmin]


class ValiderDemandeAdminView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, pk):
        demande = DemandeAdmin.objects.get(id=pk)
        password = generate_password()
        User.objects.create_user(
            username=demande.nom,
            email=demande.email,
            password=password,
            role='admin',
            telephone=demande.telephone,
            cni=demande.cni
        )
        demande.statut = 'acceptee'
        demande.save()
        send_resend_email(
            subject=f'[Votify] Compte admin validé : {demande.nom}',
            message=f'''Demande admin acceptée.

Nom : {demande.nom}
Email : {demande.email}
Mot de passe : {password}

Communiquez ces identifiants à l'administrateur.
'''
        )
        return Response({'message': 'Compte administrateur créé avec succès'})


class RefuserDemandeAdminView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, pk):
        demande = DemandeAdmin.objects.get(id=pk)
        demande.statut = 'refusee'
        demande.save()
        send_resend_email(
            subject=f'[Votify] Demande admin refusée : {demande.nom}',
            message=f'''Demande admin refusée.

Nom : {demande.nom}
Email : {demande.email}

Vous pouvez contacter le demandeur pour l'informer.
'''
        )
        return Response({'message': 'Demande refusée'})


# ── SuperAdmin ────────────────────────────────────────────

class CreerAdminDirectView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request):
        nom = request.data.get('username')
        email = request.data.get('email')
        telephone = request.data.get('telephone')
        cni = request.data.get('cni')

        if not nom or not email:
            return Response(
                {'error': "Le nom d'utilisateur et l'email sont obligatoires"},
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
        send_resend_email(
            subject=f'[Votify] Nouveau compte admin : {nom}',
            message=f'''Nouveau compte administrateur créé.

Nom : {nom}
Email : {email}
Mot de passe temporaire : {password}

Communiquez ces identifiants à l'administrateur.
'''
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


class ListeAdministrateursView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        return User.objects.filter(role='admin')


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def toggle_statut_admin(request, pk):
    try:
        administrateur = User.objects.get(pk=pk, role='admin')
    except User.DoesNotExist:
        return Response({"error": "Administrateur non trouvé"}, status=status.HTTP_404_NOT_FOUND)
    administrateur.is_active = not administrateur.is_active
    administrateur.save()
    return Response({
        "message": "Statut mis à jour avec succès",
        "is_active": administrateur.is_active
    }, status=status.HTTP_200_OK)


class StatsSuperAdminView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        total_scrutins = Scrutin.objects.count() if Scrutin else 0
        total_admins = User.objects.filter(role='admin').count()
        total_electeurs = User.objects.filter(role='electeur').count()
        demandes_attente = DemandeAdmin.objects.filter(statut='en_attente').count()
        return Response({
            'total_scrutins': total_scrutins,
            'total_admins': total_admins,
            'total_electeurs': total_electeurs,
            'demandes_attente': demandes_attente,
        })
