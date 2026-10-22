"""Registro del modelo User en el sitio de administración."""

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import BaseUserCreationForm
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm

from .models import User


class UserCreationForm(BaseUserCreationForm):
    """Formulario de alta: el usuario se identifica con su correo."""

    class Meta:
        model = User
        fields = ("email", "name", "role")


class UserChangeForm(BaseUserChangeForm):
    """Formulario de edición del usuario."""

    class Meta:
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Administración de usuarios con acción para aprobar registros.

    Las llaves del vault son de solo lectura: modificarlas a mano dejaría el
    vault del usuario ilegible.
    """

    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        "email",
        "name",
        "role",
        "is_approved",
        "is_active",
        "two_factor_enabled",
        "created_at",
    )
    list_filter = ("role", "is_approved", "is_active", "two_factor_enabled")
    search_fields = ("email", "name")
    ordering = ("-created_at",)
    list_select_related = ("role",)
    filter_horizontal = ()
    readonly_fields = (
        "id",
        "last_login",
        "created_at",
        "updated_at",
        "vault_key_user",
        "vault_key_admin",
        "public_key",
    )

    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        ("Datos personales", {"fields": ("name", "phone")}),
        (
            "Acceso",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_approved",
                    "two_factor_enabled",
                    "email_verified_at",
                )
            },
        ),
        (
            "Llaves del vault",
            {"fields": ("vault_key_user", "vault_key_admin", "public_key")},
        ),
        ("Fechas", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "name", "role", "password1", "password2"),
            },
        ),
    )

    actions = ["approve_users"]

    @admin.action(description="Aprobar usuarios seleccionados")
    def approve_users(self, request, queryset):
        """Marca como aprobados los usuarios pendientes seleccionados."""
        updated = queryset.filter(is_approved=False).update(is_approved=True)
        self.message_user(
            request,
            f"{updated} usuario(s) aprobado(s).",
            messages.SUCCESS,
        )