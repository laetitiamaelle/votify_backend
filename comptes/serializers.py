# comptes/serializers.py — ajouter le UserSerializer si pas encore présent
from rest_framework import serializers
from .models import User, DemandeAdmin
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# comptes/serializers.py
from rest_framework import serializers
from .models import User

from rest_framework import serializers
from .models import User
from django.core.mail import send_mail
# On importe la même fonction de génération que tes vues utilisent
from .services import generate_password  

class RegisterSerializer(serializers.ModelSerializer):
    # On mappe explicitement les données envoyées par ton formulaire Angular
    first_name = serializers.CharField(required=True)
    telephone = serializers.CharField(required=True)
    cni = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'email', 'telephone', 'cni']

    def create(self, validated_data):
        email = validated_data['email']
        first_name = validated_data.get('first_name', '')
        
        # 1. Génération du username requis par AbstractUser (basé sur l'email)
        generated_username = email.split('@')[0]
        if User.objects.filter(username=generated_username).exists():
            import uuid
            generated_username = f"{generated_username}_{uuid.uuid4().hex[:4]}"

        # 2. Utilisation de TA fonction pour générer le mot de passe secret
        password = generate_password()

        # 3. Création de l'utilisateur Électeur
        user = User.objects.create_user(
            username=generated_username,
            email=email,
            password=password,
            first_name=first_name,
            telephone=validated_data.get('telephone', ''),
            cni=validated_data.get('cni', ''),
            role='electeur',
            must_change_password=True # Force l'électeur à changer son mot de passe au premier login
        )

        # 4. Envoi de l'email (sur le même modèle que tes vues d'administration)
        send_mail(
            subject='Votre compte Électeur Votify',
            message=f'''Bonjour {first_name},

Votre compte électeur a été créé avec succès sur l'application Votify.

Voici vos paramètres de connexion :
Email : {email}
Mot de passe temporaire : {password}

Veuillez modifier votre mot de passe dès votre première connexion pour sécuriser votre accès.
''',
            from_email='laetitiamaelle740@gmail.com', # Même adresse d'expédition que tes autres vues
            recipient_list=[email],
            fail_silently=False
        )

        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'telephone', 'is_active']
        read_only_fields = ['id', 'email', 'role', 'is_active']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)


class DemandeAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandeAdmin
        fields = ['id', 'nom', 'email', 'telephone', 'cni', 'organisation', 'motif', 'statut', 'date_creation']
        read_only_fields = ['id', 'statut', 'date_creation']


# comptes/serializers.py

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Ce bloc ajoute les infos *à l'intérieur* du jeton JWT crypté
        token['role'] = user.role
        token['username'] = user.username
        token['must_change_password'] = user.must_change_password
        return token

    def validate(self, attrs):
        # Ce bloc modifie le corps de la réponse JSON renvoyée lors du POST /login
        data = super().validate(attrs)
        
        # On injecte l'objet 'user' attendu par ton code Angular !
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
            'is_superuser': self.user.is_superuser,
            'must_change_password': self.user.must_change_password
        }
        
        return data