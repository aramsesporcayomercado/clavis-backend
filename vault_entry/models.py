"""Modelos de la aplicación ``passwords``."""

import uuid

from django.conf import settings
from django.db import models


class VaultEntry(models.Model):
    """Entrada del vault de un usuario.

    ``encrypted_data`` guarda un único bloque cifrado en el cliente con el
    nombre, el correo de la cuenta, la contraseña, la URL y las notas. El
    servidor nunca ve esos datos en claro, por eso no hay columnas separadas.
    ``is_active`` implementa el borrado lógico: una entrada dada de baja se
    oculta, pero se puede recuperar.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="vault_entries",
    )
    encrypted_data = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["user", "is_active"],
                name="passwords_entry_user_idx",
            ),
        ]

    def __str__(self) -> str:
        # El nombre está cifrado, así que solo se identifica por su id.
        return f"VaultEntry {self.id}"