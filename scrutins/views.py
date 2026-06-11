from rest_framework import generics

from .models import Scrutin

from .serializers import ScrutinSerializer

from .permissions import IsAdmin
from django_filters.rest_framework import DjangoFilterBackend


# création d’un scrutin
class CreerScrutinView(generics.CreateAPIView):

    serializer_class = ScrutinSerializer

    permission_classes = [IsAdmin]

    def perform_create(self, serializer):

        # admin connecté automatiquement enregistré
        serializer.save(admin=self.request.user)


# liste des scrutins créés par l’admin connecté
class MesScrutinsView(generics.ListAPIView):

    serializer_class = ScrutinSerializer

    permission_classes = [IsAdmin]

    def get_queryset(self):

        return Scrutin.objects.filter(
            admin=self.request.user
        )

# liste des scrutins publics
class ListeScrutinsPublicsView(generics.ListAPIView):

    serializer_class = ScrutinSerializer

    queryset = Scrutin.objects.filter(actif=True)

    filter_backends = [DjangoFilterBackend]

    filterset_fields = ['titre']

# détails d’un scrutin
class DetailScrutinView(generics.RetrieveAPIView):

    queryset = Scrutin.objects.all()

    serializer_class = ScrutinSerializer
# Create your views here.

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Scrutin
from .serializers import ScrutinSerializer
from .permissions import IsAdmin
from django_filters.rest_framework import DjangoFilterBackend

from candidats.models import Candidat
from vote.models import InscriptionScrutin, Vote


# création d'un scrutin
class CreerScrutinView(generics.CreateAPIView):
    serializer_class = ScrutinSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)


# liste des scrutins créés par l'admin connecté
class MesScrutinsView(generics.ListAPIView):
    serializer_class = ScrutinSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return Scrutin.objects.filter(admin=self.request.user).order_by('-date_creation')


# modifier un scrutin
class ModifierScrutinView(generics.UpdateAPIView):
    queryset = Scrutin.objects.all()
    serializer_class = ScrutinSerializer
    permission_classes = [IsAdmin]


# supprimer un scrutin
class SupprimerScrutinView(generics.DestroyAPIView):
    queryset = Scrutin.objects.all()
    permission_classes = [IsAdmin]


# liste des scrutins publics
class ListeScrutinsPublicsView(generics.ListAPIView):
    serializer_class = ScrutinSerializer
    queryset = Scrutin.objects.filter(actif=True)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['titre']


# détails d'un scrutin
class DetailScrutinView(generics.RetrieveAPIView):
    queryset = Scrutin.objects.all()
    serializer_class = ScrutinSerializer


# statistiques globales pour le dashboard admin
class StatsDashboardView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        admin = request.user

        # scrutins de cet admin
        scrutins = Scrutin.objects.filter(admin=admin)
        nb_scrutins_actifs = scrutins.filter(actif=True).count()

        # candidats sur les scrutins de cet admin
        nb_candidats = Candidat.objects.filter(scrutin__admin=admin).count()

        # inscrits (acceptés) sur les scrutins de cet admin
        nb_inscrits = InscriptionScrutin.objects.filter(
            scrutin__admin=admin,
            statut='accepte'
        ).count()

        # votes exprimés sur les scrutins de cet admin
        nb_votes = Vote.objects.filter(scrutin__admin=admin).count()

        return Response({
            'scrutins_actifs': nb_scrutins_actifs,
            'candidats': nb_candidats,
            'inscrits': nb_inscrits,
            'votes_exprimes': nb_votes,
        })

