from rest_framework import serializers
from .models import Candidat


class CandidatSerializer(serializers.ModelSerializer):

    # URL complète de la photo si elle existe
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Candidat
        fields = [
            'id',
            'scrutin',
            'nom',
            'poste',
            'description',
            'photo',
            'photo_url',
            'date_creation',
        ]
        read_only_fields = ['id', 'date_creation', 'photo_url']
        extra_kwargs = {
            'photo': {'write_only': True, 'required': False},
        }

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return None
