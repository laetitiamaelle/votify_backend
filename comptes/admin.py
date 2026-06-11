from django.contrib import admin
from .models import User # <-- Importe ton modèle personnalisé ici

# Enregistre ton modèle pour qu'il soit visible dans l'admin
admin.site.register(User)