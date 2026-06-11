from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Candidat
from .serializers import CandidatSerializer
from .permissions import IsAdmin


class AjouterCandidatView(generics.CreateAPIView):
    serializer_class = CandidatSerializer
    permission_classes = [IsAdmin]
    # MultiPartParser nécessaire pour l'upload de photo
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class ListeCandidatsScrutinView(generics.ListAPIView):
    serializer_class = CandidatSerializer

    def get_queryset(self):
        return Candidat.objects.filter(scrutin_id=self.kwargs['scrutin_id'])

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class ModifierCandidatView(generics.UpdateAPIView):
    queryset = Candidat.objects.all()
    serializer_class = CandidatSerializer
    permission_classes = [IsAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class SupprimerCandidatView(generics.DestroyAPIView):
    queryset = Candidat.objects.all()
    permission_classes = [IsAdmin]
