from django.core.management.base import BaseCommand
from comptes.models import User


class Command(BaseCommand):
    help = "Créer le super administrateur"

    def handle(self, *args, **kwargs):

        email = "laetitiamaelle740@gmail.com"

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING("Le superadmin existe déjà")
            )
            return

        user = User(
            username="maelle",
            email="laetitiamaelle740@gmail.com",
            role="admin",  # ton modèle ne possède pas de rôle superadmin
            is_staff=True,
            is_superuser=True,
            is_verified=True,
            is_active=True,
        )

        # Remplace ce mot de passe par celui que tu veux
        user.set_password("motdepasse")
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                "Superadmin créé avec succès : laetitiamaelle740@gmail.com"
            )
        )