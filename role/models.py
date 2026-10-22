"""Modelos de la aplicación ``role``."""

import uuid

from django.db import models


class Role(models.Model):
    """Rol de acceso de un usuario.

    Los roles ``familiar`` y ``admin`` son los que el código del sistema
    referencia (ver :class:`Name`). El modelo permite registrar roles
    adicionales a futuro.
    """

    class Name(models.TextChoices):
        """Nombres de los roles que el código del sistema utiliza."""

        FAMILIAR = "familiar", "Familiar"
        ADMIN = "admin", "Administrador"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name