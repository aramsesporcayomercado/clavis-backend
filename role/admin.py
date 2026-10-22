"""Registro del modelo Role en el sitio de administración."""

from django.contrib import admin

from .models import Role

SYSTEM_ROLES = (Role.Name.ADMIN, Role.Name.FAMILIAR)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Administración de roles.

    Los roles que el sistema referencia en el código no pueden renombrarse ni
    eliminarse, porque los privilegios dependen de su nombre.
    """

    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    readonly_fields = ("id", "created_at")

    def get_readonly_fields(self, request, obj=None):
        """Bloquea la edición del nombre en los roles del sistema."""
        readonly = list(super().get_readonly_fields(request, obj))
        if obj is not None and obj.name in SYSTEM_ROLES:
            readonly.append("name")
        return readonly

    def has_delete_permission(self, request, obj=None):
        """Impide eliminar los roles del sistema."""
        if obj is not None and obj.name in SYSTEM_ROLES:
            return False
        return super().has_delete_permission(request, obj)