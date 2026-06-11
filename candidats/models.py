from django.db import models
from scrutins.models import Scrutin


class Candidat(models.Model):

    scrutin = models.ForeignKey(
        Scrutin,
        on_delete=models.CASCADE,
        related_name='candidats'
    )

    nom = models.CharField(max_length=255)

    poste = models.CharField(max_length=255, blank=True, default='')

    description = models.TextField(blank=True, default='')

    photo = models.ImageField(
        upload_to='candidats/',
        blank=True,
        null=True
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom
