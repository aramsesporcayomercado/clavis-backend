"""Modelos de la aplicación ``users``."""

import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models

from role.models import Role


class UserManager(BaseUserManager):
    """Administrador de :class:`User`; el inicio de sesión usa el correo."""

    use_in_migrations = True

    def create_user(self, email: str, password: str | None = None, **extra):
        """Crea un usuario estándar pendiente de aprobación.

        Args:
            email: Correo único que identifica al usuario en el login.
            password: Contraseña de login; Django almacena solo su hash.
            **extra: Cualquier otro campo de :class:`User`.

        Returns:
            El usuario creado.

        Raises:
            ValueError: Si el correo viene vacío.
        """
        if not email:
            raise ValueError("El correo es obligatorio.")
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra):
        """Crea un usuario con rol ``admin`` ya aprobado.

        Si el rol ``admin`` no existe todavía, lo crea.
        """
        if "role" not in extra:
            extra["role"], _ = Role.objects.get_or_create(name=Role.Name.ADMIN)
        extra.setdefault("is_approved", True)
        return self.create_user(email, password, **extra)

class User(AbstractBaseUser):
    """Usuario de Clavis.

    El rol es la única fuente de privilegios. ``is_active`` indica si la cuenta
    está habilitada (el borrado lógico lo pone en falso) e ``is_approved``
    indica si el administrador ya autorizó el registro.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    vault_key_user = models.TextField(blank=True)
    vault_key_admin = models.TextField(blank=True)
    public_key = models.TextField(blank=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="users")
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    class Meta:
        indexes = [
            models.Index(
                fields=["is_approved", "is_active"],
                name="users_user_approval_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.email

    @property
    def is_admin(self) -> bool:
        """Indica si el usuario tiene el rol ``admin``."""
        return self.role.name == Role.Name.ADMIN

    @property
    def is_staff(self) -> bool:
        """Permite el acceso al sitio de administración de Django (solo admin)."""
        return self.is_admin

    def has_perm(self, perm: str, obj=None) -> bool:
        """Un administrador activo posee todos los permisos de Django."""
        return self.is_active and self.is_admin

    def has_module_perms(self, app_label: str) -> bool:
        """Un administrador activo ve todas las aplicaciones en el admin."""
        return self.is_active and self.is_admin