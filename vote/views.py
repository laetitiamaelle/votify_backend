from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .models import InscriptionScrutin, Vote, Notification
from .serializers import InscriptionScrutinSerializer, VoteSerializer, NotificationSerializer
from .permissions import IsElecteur, IsAdmin

from candidats.models import Candidat


# ── ÉLECTEUR ─────────────────────────────────────────────────

class InscriptionScrutinView(generics.CreateAPIView):
    serializer_class = InscriptionScrutinSerializer
    permission_classes = [IsElecteur]

    def perform_create(self, serializer):
        inscription = serializer.save(electeur=self.request.user)
        # Notifier l'admin du scrutin
        admin = inscription.scrutin.admin
        Notification.objects.create(
            destinataire=admin,
            message=f"{self.request.user.username} a demandé l'inscription au scrutin « {inscription.scrutin.titre} ».",
            type='inscription_demande',
            scrutin=inscription.scrutin,
            inscription=inscription,
        )


class MesInscriptionsView(generics.ListAPIView):
    serializer_class = InscriptionScrutinSerializer
    permission_classes = [IsElecteur]

    def get_queryset(self):
        return InscriptionScrutin.objects.filter(
            electeur=self.request.user
        ).select_related('electeur', 'scrutin')


class VoterView(generics.CreateAPIView):
    serializer_class = VoteSerializer
    permission_classes = [IsElecteur]

    def create(self, request, *args, **kwargs):
        candidat_id = request.data.get('candidat')
        try:
            candidat = Candidat.objects.get(id=candidat_id)
        except Candidat.DoesNotExist:
            return Response({'error': 'Candidat introuvable'}, status=status.HTTP_404_NOT_FOUND)

        scrutin = candidat.scrutin

        if not InscriptionScrutin.objects.filter(
            electeur=request.user, scrutin=scrutin, statut='accepte'
        ).exists():
            return Response({'error': 'Inscription non validée'}, status=status.HTTP_400_BAD_REQUEST)

        if Vote.objects.filter(electeur=request.user, scrutin=scrutin).exists():
            return Response({'error': 'Vous avez déjà voté'}, status=status.HTTP_400_BAD_REQUEST)

        Vote.objects.create(electeur=request.user, scrutin=scrutin, candidat=candidat)
        return Response({'message': 'Vote effectué avec succès'})


# ── ADMIN ─────────────────────────────────────────────────────

class InscriptionsEnAttenteView(generics.ListAPIView):
    serializer_class = InscriptionScrutinSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return InscriptionScrutin.objects.filter(
            scrutin__admin=self.request.user,
            statut='en_attente'
        ).select_related('electeur', 'scrutin')


class AccepterInscriptionView(generics.UpdateAPIView):
    queryset = InscriptionScrutin.objects.all()
    serializer_class = InscriptionScrutinSerializer
    permission_classes = [IsAdmin]

    def update(self, request, *args, **kwargs):
        inscription = self.get_object()
        inscription.statut = 'accepte'
        inscription.save()
        # Notifier l'électeur
        Notification.objects.create(
            destinataire=inscription.electeur,
            message=f"Votre inscription au scrutin « {inscription.scrutin.titre} » a été acceptée. Vous pouvez maintenant voter.",
            type='inscription_acceptee',
            scrutin=inscription.scrutin,
            inscription=inscription,
        )
        return Response({'message': 'Inscription acceptée'})


class RefuserInscriptionView(generics.UpdateAPIView):
    queryset = InscriptionScrutin.objects.all()
    serializer_class = InscriptionScrutinSerializer
    permission_classes = [IsAdmin]

    def update(self, request, *args, **kwargs):
        inscription = self.get_object()
        inscription.statut = 'refuse'
        inscription.save()
        # Notifier l'électeur
        Notification.objects.create(
            destinataire=inscription.electeur,
            message=f"Votre inscription au scrutin « {inscription.scrutin.titre} » a été refusée.",
            type='inscription_refusee',
            scrutin=inscription.scrutin,
            inscription=inscription,
        )
        return Response({'message': 'Inscription refusée'})


# ── NOTIFICATIONS ─────────────────────────────────────────────

class MesNotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(
            destinataire=self.request.user
        ).order_by('-date_creation')


class NombreNotificationsNonLuesView(APIView):
    def get(self, request):
        count = Notification.objects.filter(
            destinataire=request.user, lue=False
        ).count()
        return Response({'non_lues': count})


class MarquerNotificationsLuesView(APIView):
    def post(self, request):
        Notification.objects.filter(
            destinataire=request.user, lue=False
        ).update(lue=True)
        return Response({'message': 'Notifications marquées comme lues'})


# ── RÉSULTATS ─────────────────────────────────────────────────

class ResultatsScrutinView(APIView):
    def get(self, request, scrutin_id):
        candidats = Candidat.objects.filter(scrutin_id=scrutin_id)
        total_votes = Vote.objects.filter(scrutin_id=scrutin_id).count()
        resultats = []

        for candidat in candidats:
            nombre_votes = Vote.objects.filter(candidat=candidat).count()
            pourcentage = round((nombre_votes / total_votes) * 100, 2) if total_votes > 0 else 0
            resultats.append({
                'candidat_id': candidat.id,
                'candidat':    candidat.nom,
                'poste':       candidat.poste,
                'photo_url':   request.build_absolute_uri(candidat.photo.url) if candidat.photo else None,
                'votes':       nombre_votes,
                'pourcentage': pourcentage,
            })

        resultats.sort(key=lambda x: x['votes'], reverse=True)
        return Response({'total_votes': total_votes, 'resultats': resultats})
