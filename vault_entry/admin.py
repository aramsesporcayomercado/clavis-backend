"""Administración de la aplicación ``passwords``."""

from django.contrib import admin

from .models import VaultEntry


@admin.register(VaultEntry)
class VaultEntryAdmin(admin.ModelAdmin):
    """Vista de solo lectura de las entradas del vault.

    No se muestra ``encrypted_data``: editarlo desde el panel no tiene sentido
    y tampoco hace falta exponer el bloque cifrado. Las entradas se crean,
    editan y dan de baja únicamente desde la aplicación.
    """

    exclude = ("encrypted_data",)
    list_display = ("id", "user", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    list_select_related = ("user",)
    search_fields = ("user__email",)

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False