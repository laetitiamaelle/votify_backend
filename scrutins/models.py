from django.db import models

from comptes.models import User


class Scrutin(models.Model):

    # administrateur qui a créé le scrutin
    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='scrutins'
    )

    # titre du scrutin
    titre = models.CharField(max_length=255)

    # description du scrutin
    description = models.TextField()

    # date de début du vote
    date_debut = models.DateTimeField()

    # date de fin du vote
    date_fin = models.DateTimeField()

    # permet d'activer ou désactiver un scrutin
    actif = models.BooleanField(default=True)

    # date de création automatique
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return self.titre
# Create your models here.
