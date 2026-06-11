from django.db import models
from comptes.models import User
from scrutins.models import Scrutin
from candidats.models import Candidat


class InscriptionScrutin(models.Model):
    STATUS_CHOICES = (
        ('en_attente', 'En attente'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
    )
    electeur           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inscriptions')
    scrutin            = models.ForeignKey(Scrutin, on_delete=models.CASCADE, related_name='inscriptions')
    nom_electeur       = models.CharField(max_length=255, blank=True, default='')
    organisation       = models.CharField(max_length=255, blank=True, default='')
    statut             = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    date_inscription   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['electeur', 'scrutin']

    def __str__(self):
        return f"{self.electeur.username} - {self.scrutin.titre}"


class Vote(models.Model):
    electeur   = models.ForeignKey(User, on_delete=models.CASCADE)
    scrutin    = models.ForeignKey(Scrutin, on_delete=models.CASCADE)
    candidat   = models.ForeignKey(Candidat, on_delete=models.CASCADE)
    date_vote  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['electeur', 'scrutin']

    def __str__(self):
        return f"{self.electeur.username} a voté"


class Notification(models.Model):
    TYPE_CHOICES = (
        ('inscription_demande',  'Demande d\'inscription'),
        ('inscription_acceptee', 'Inscription acceptée'),
        ('inscription_refusee',  'Inscription refusée'),
    )
    destinataire   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message        = models.TextField()
    type           = models.CharField(max_length=30, choices=TYPE_CHOICES)
    scrutin        = models.ForeignKey(Scrutin, on_delete=models.CASCADE, null=True, blank=True)
    inscription    = models.ForeignKey(InscriptionScrutin, on_delete=models.SET_NULL, null=True, blank=True)
    lue            = models.BooleanField(default=False)
    date_creation  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"Notif pour {self.destinataire.username} — {self.type}"
