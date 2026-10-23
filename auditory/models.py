"""Modelos de la aplicación ``auditory``."""

import uuid

from django.conf import settings
from django.db import models


class AuditLogQuerySet(models.QuerySet):
    """QuerySet que impide modificar o borrar registros de auditoría."""

    def update(self, **kwargs):
        raise PermissionError("Los registros de auditoría no se pueden modificar.")

    def delete(self):
        raise PermissionError("Los registros de auditoría no se pueden borrar.")


class AuditLog(models.Model):
    """Registro de trazabilidad de las acciones sobre el vault.

    ``actor`` es quien realizó la acción y ``target_user`` es el dueño de lo
    afectado, cuando es distinto (por ejemplo, un administrador que ve la
    contraseña de un familiar). ``ip_address`` indica desde dónde se hizo.

    El registro es de solo anexar: una vez creado no se edita ni se borra,
    ni desde el panel ni desde el ORM (``save`` sobre un registro existente,
    ``delete`` y las operaciones masivas ``update``/``delete`` lanzan
    ``PermissionError``). Esto no sustituye a la protección en la base de
    datos: para eso hay que quitar ``UPDATE`` y ``DELETE`` sobre esta tabla al
    rol de PostgreSQL que usa la aplicación.

    ``name`` es texto libre; :class:`Name` solo reúne los nombres que el
    código del sistema ya usa.
    """

    class Name(models.TextChoices):
        """Nombres de acción que el código del sistema utiliza."""

        CREATE_ENTRY = "create_entry", "Creó una entrada"
        UPDATE_ENTRY = "update_entry", "Editó una entrada"
        VIEW_ENTRY = "view_entry", "Vio una entrada"
        DELETE_ENTRY = "delete_entry", "Dio de baja una entrada"
        ADMIN_VIEW_ENTRY = "admin_view_entry", "Un administrador vio una entrada ajena"

    class Status(models.TextChoices):
        """Resultado de la acción."""

        SUCCESS = "success", "Éxito"
        FAILURE = "failure", "Fallo"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="audit_actions",
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="audit_received",
    )
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = AuditLogQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["actor", "created_at"],
                name="auditory_actor_created_idx",
            ),
            models.Index(
                fields=["target_user", "created_at"],
                name="auditory_target_created_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.created_at:%Y-%m-%d %H:%M})"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise PermissionError("Los registros de auditoría no se pueden modificar.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError("Los registros de auditoría no se pueden borrar.")