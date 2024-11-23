from rest_framework import serializers
from .models import Categoria, Autor, Livro, Colecao

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ('id',
                  'nome')

class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = ('id',
                  'name')


class LivroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livro
        fields = ("id", "titulo", "autor", "categoria", "publicado_em")


class ColecaoSerializer(serializers.ModelSerializer):
    # Display the owner's username (read-only)
    colecionador = serializers.ReadOnlyField(source="owner.username")
    owner = serializers.ReadOnlyField(source="owner.username")
    class Meta:
        model = Colecao
        fields = ("id", "nome", "descricao", "livros", "colecionador", "owner")

# ADICIONANDO SERIALIZADORES DE USUARIOS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class UserColecaoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Colecao
        fields = (
            'url',
            'name'
            )

class UserSerializer(serializers.HyperlinkedModelSerializer):
    Colecao = UserColecaoSerializer(
        many=True,
        read_only=True)
    class Meta:
        # model = User
        fields = (
            'url',
            'pk',
            'username',
            'colecao')
