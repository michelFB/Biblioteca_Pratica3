from rest_framework import permissions


class IsCurrentUserOwnerOrReadOnly(permissions.BasePermission):
    """
    Permissão customizada para permitir que apenas o colecionador possa modificar a coleção.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            # Permissões de leitura são permitidas para qualquer requisição
            # então vamos sempre permitir GET, HEAD ou OPTIONS.
            return True
        else:
            # Permissões de escrita são permitidas apenas ao colecionador da coleção
            return obj.owner == request.user
