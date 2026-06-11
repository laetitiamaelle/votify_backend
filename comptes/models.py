from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('electeur', 'Electeur'),
    )
   

    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        blank=True,
        null=True,
        default='electeur'
    )
    email=models.EmailField( unique=True)

    telephone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    cni = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    is_verified = models.BooleanField(default=False)
   
    must_change_password = models.BooleanField(default=False)
    USERNAME_FIELD = 'email' # <-- Dit à Django d'utiliser l'email comme identifiant
    REQUIRED_FIELDS = ['username'] # Obligatoire pour AbstractUser
    def __str__(self):
        return self.username
    

class DemandeAdmin(models.Model):

    nom = models.CharField(max_length=150)

    email = models.EmailField()

    telephone = models.CharField(max_length=20)

    cni = models.CharField(max_length=100)

    organisation = models.CharField(max_length=255)

    motif = models.TextField()

    statut = models.CharField(
        max_length=20,
        choices=[
            ('en_attente', 'En attente'),
            ('acceptee', 'Acceptée'),
            ('refusee', 'Refusée')
        ],
        default='en_attente'
    )

    date_creation = models.DateTimeField(auto_now_add=True)