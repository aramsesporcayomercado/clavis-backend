"""Modelos de la aplicación ``security_events``."""

import uuid

from django.conf import settings
from django.db import models


class SecurityEvent(models.Model):
    """Evento de seguridad registrado para generar alertas.

    ``name`` es texto libre: la base de datos acepta eventos nuevos sin
    migración. :class:`Name` solo reúne los nombres que el código del sistema
    ya usa, para no escribirlos a mano en cada lugar.

    ``user`` es opcional porque un login con un correo inexistente no
    pertenece a ningún usuario; en ese caso se guarda el correo intentado en
    ``attempted_email``.
    """

    class Name(models.TextChoices):
        """Nombres de evento que el código del sistema utiliza."""

        LOGIN_FAILED = "login_failed", "Login fallido"
        LOGIN_UNKNOWN_EMAIL = "login_unknown_email", "Login con correo inexistente"
        REPEATED_LOGIN_ATTEMPTS = (
            "repeated_login_attempts",
            "Intentos de login repetidos",
        )
        NEW_DEVICE = "new_device", "Dispositivo nuevo"
        NEW_IP = "new_ip", "IP nueva"
        MASS_READ = "mass_read", "Lecturas masivas"
        HONEYPOT_HIT = "honeypot_hit", "Acceso a ruta trampa"

    class Status(models.TextChoices):
        """Estados posibles de un evento."""

        PENDING = "pending", "Pendiente"
        RESOLVED = "resolved", "Resuelto"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="security_events",
    )
    # CharField y no EmailField: un correo mal escrito no pasaría la validación
    # y el evento no se guardaría.
    attempted_email = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    # Lo manda el cliente (Flutter): se acota para que nadie pueda llenar la
    # base de datos con texto sin límite. El serializer debe truncarlo.
    device = models.CharField(max_length=512, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["user", "created_at"],
                name="secevents_user_created_idx",
            ),
            models.Index(
                fields=["status", "created_at"],
                name="secevents_status_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.created_at:%Y-%m-%d %H:%M})"