"""Administración de la aplicación ``auditory``."""

from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Vista de solo lectura del registro de auditoría.

    Sin agregar, editar ni borrar desde el panel, para que el registro sea
    confiable. Esto no impide cambios desde código o directo en la base de
    datos; para eso se necesitarían permisos a nivel de PostgreSQL.
    """

    list_display = ("created_at", "name", "actor", "target_user", "status")
    list_filter = ("status", "name")
    list_select_related = ("actor", "target_user")
    search_fields = ("actor__email", "target_user__email")
    date_hierarchy = "created_at"

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False