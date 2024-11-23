from django.utils.http import urlencode
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Colecao, Autor, Categoria, Livro
from core import views
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import pytest


class ColecaoTests(APITestCase):

    def create_user_and_set_token_credentials(self):
        self.user1 = User.objects.create_user(username="user1", password="password1")
        self.user2 = User.objects.create_user(username="user2", password="password2")

    def create_livros(self):
        autor1 = Autor.objects.create(name="J.R.R. Tolkien")
        autor2 = Autor.objects.create(name="Tanebaw")
        categoria1 = Categoria.objects.create(nome="Romance")
        categoria2 = Categoria.objects.create(nome="Fantasia")
        self.livro1 = Livro.objects.create(titulo = "O Senhor dos aneis",autor = autor1,categoria = categoria1,publicado_em = "1954-07-29",)
        self.livro2 = Livro.objects.create( titulo="Eletronica básica", autor=autor2, categoria=categoria2, publicado_em="2500-07-29",)

    def setUp(self):
        self.colecoes_url = reverse("colecao-list")
        self.create_user_and_set_token_credentials()
        self.create_livros()

    def test_create_collection_auth(self):
        # Criando token para usuário 1 e passando as credenciais de autorização via cabeçalho HTTP
        token = Token.objects.create(user=self.user1)
        self.client.credentials(HTTP_AUTHORIZATION="Token {0}".format(token.key))
        # Criando dados de coleção e submentendo via metodo post
        data = {"nome": "nome","descricao": "descricao","livros": [self.livro1.pk],}
        print("Criando coleção para POST: ",data)
        response = self.client.post(self.colecoes_url, data, format="json")
        print(response.data)
        print("Coleção criada com sucesso via POST! 201")
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(1, Colecao.objects.count())
        self.assertEqual(response.data["nome"], Colecao.objects.get().nome)
        self.assertEqual(response.data["descricao"], Colecao.objects.get().descricao)
        self.assertEqual(response.data["livros"],
            list(Colecao.objects.get().livros.values_list("pk", flat=True)),
        )
        self.assertEqual(response.data["colecionador"], self.user1.username)
        self.assertEqual(response.data["owner"], self.user1.username)

    def test_create_collection_no_auth(self):
        data = {"nome": "nome","descricao": "descricao","livros": [self.livro1.pk],}
        response = self.client.post(self.colecoes_url, data, format="json")
        print("Não foi possível fazer o POST! Usuário não autorizado. 401")
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code) # Erro de autenticação

    def test_edit_user_collection(self):
        # Criando token para usuário 1 e passando as credenciais de autorização via cabeçalho HTTP
        token = Token.objects.create(user=self.user1)
        self.client.credentials(HTTP_AUTHORIZATION="Token {0}".format(token.key))
        # Criando uma coleção pertencente ao usuário 1
        colecao = Colecao.objects.create(nome="Minha Coleção", descricao="Descrição",
             colecionador = self.user1, owner = self.user1)
        print("coleção criada: ",colecao)
        # Criando a url de chamada para atualização pelo id da coleção e novos dados
        url = f"{self.colecoes_url}{colecao.id}/"
        data = {"nome": "Nova Coleção"}
        print("dados para atualização: ", data)
        # Submetendo atualização de conferindo se o dado foi atualizado
        response = self.client.patch(url, data)
        print("Coleção Atualizada com Sucesso! 200. Retorno da atualização 1: ", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nome"], "Nova Coleção")
        # Criando token para usuário 2 e passando as credenciais de autorização via cabeçalho HTTP
        token = Token.objects.create(user=self.user2)
        self.client.credentials(HTTP_AUTHORIZATION="Token {0}".format(token.key))
        # Criando novos dados para atualização
        data = {"nome": "Coleção Editada"}
        print("Novos dados para atualização: ",data)
        response = self.client.patch(url, data)
        print("Não foi possível atualizar a coleção! Usuário não autorizado. 403. Retorno da atualização 2: ", response.data)
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )  # recusando a ação devido a problemas de permissão

    def test_delete_user_collection(self):
        # Criando uma coleção pertencente ao usuário 1
        colecao = Colecao.objects.create(nome="Minha Coleção", descricao="Descrição",
            colecionador = self.user1, owner = self.user1)
        print("Coleção criada: ", colecao)
        # Criando token para usuário 2 e passando as credenciais de autorização via cabeçalho HTTP
        token = Token.objects.create(user=self.user2)
        self.client.credentials(HTTP_AUTHORIZATION="Token {0}".format(token.key))
        # Requisição de delete para usuario 2
        url = f"{self.colecoes_url}{colecao.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        print("Usuário sem permissão para exclusão! 403")
        # Criando token para usuário 1 e passando as credenciais de autorização via cabeçalho HTTP
        token = Token.objects.create(user=self.user1)
        self.client.credentials(HTTP_AUTHORIZATION="Token {0}".format(token.key))
        # Requisição de delete para usuário 1
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)  # requisição foi bem-sucedida para DELETE ou PUT
        self.assertFalse(Colecao.objects.filter(id=colecao.id).exists())
        print("coleção excluída com Sucesso 204")

    def test_list_collections(self):
        response = self.client.get(self.colecoes_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
