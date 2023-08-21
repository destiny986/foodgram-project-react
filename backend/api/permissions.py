from rest_framework.permissions import SAFE_METHODS, BasePermission


class CustomPermission(BasePermission):
    """
    У неаутентифицированных пользователей доступ к API только на чтение.
    Аутентифицированным пользователям разрешено изменение и удаление
    своего контента; в остальных случаях доступ предоставляется только
    для чтения.
    """

    def has_permission(self, request, view):
        """Вызывается для всех запросов."""
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Вызывается только при обращении к уже существующему объекту.
        """
        return (
            request.user.is_superuser
            or request.method in SAFE_METHODS
            or obj.author == request.user
        )
