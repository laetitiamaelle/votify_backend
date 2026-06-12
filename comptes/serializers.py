# comptes/serializers.py
from rest_framework import serializers
from .models import User, DemandeAdmin
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.mail import send_mail
from .services import generate_password  


class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    telephone = serializers.CharField(required=True)
    cni = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'email', 'telephone', 'cni']

    def create(self, validated_data):
        email = validated_data['email']
        first_name = validated_data.get('first_name', '')
        
        generated_username = email.split('@')[0]
        if User.objects.filter(username=generated_username).exists():
            import uuid
            generated_username = f"{generated_username}_{uuid.uuid4().hex[:4]}"

        password = generate_password()

        user = User.objects.create_user(
            username=generated_username,
            email=email,
            password=password,
            first_name=first_name,
            telephone=validated_data.get('telephone', ''),
            cni=validated_data.get('cni', ''),
            role='electeur',
            must_change_password=True
        )

        send_mail(
            subject='Votre compte Électeur Votify',
            message=f'''Bonjour {first_name},

Votre compte électeur a été créé avec succès sur l'application Votify.

Voici vos paramètres de connexion :
Email : {email}
Mot de passe temporaire : {password}

Veuillez modifier votre mot de passe dès votre première connexion pour sécuriser votre accès.
''',
            from_email='onboarding@resend.dev',
            recipient_list=[email],
            fail_silently=True
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


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['username'] = user.username
        token['must_change_password'] = user.must_change_password
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
            'is_superuser': self.user.is_superuser,
            'must_change_password': self.user.must_change_password
        }
        return data
