"""Administración de la aplicación ``security_events``."""

from django.contrib import admin

from .models import SecurityEvent


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    """Eventos de seguridad: lo único editable desde el panel es ``status``.

    Así el administrador puede marcar un evento como resuelto sin poder
    alterar lo que realmente ocurrió. Tampoco se pueden crear ni borrar.
    """

    list_display = ("created_at", "name", "user", "attempted_email", "ip_address", "status")
    list_filter = ("status", "name")
    list_select_related = ("user",)
    search_fields = ("user__email", "attempted_email", "ip_address")
    date_hierarchy = "created_at"
    readonly_fields = (
        "user",
        "attempted_email",
        "name",
        "description",
        "ip_address",
        "device",
        "created_at",
    )

    def has_add_permission(self, request) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False