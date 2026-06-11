from rest_framework import serializers

from .models import Scrutin


class ScrutinSerializer(serializers.ModelSerializer):

    class Meta:
        model = Scrutin
        fields = [
            'id',
            'admin',
            'titre',
            'description',
            'date_debut',
            'date_fin',
            'actif',
            'date_creation',
        ]
        read_only_fields = ['id', 'admin', 'date_creation']
