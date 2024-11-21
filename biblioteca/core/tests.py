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

        self.livro1 = Livro.objects.create(
            titulo = "O Senhor dos aneis",
            autor = autor1,
            categoria = categoria1,
            publicado_em = "1954-07-29",
        )
        self.livro2 = Livro.objects.create(
            titulo="Eletronica básica",
            autor=autor2,
            categoria=categoria2,
            publicado_em="2500-07-29",
        )

    def setUp(self):
        self.create_user_and_set_token_credentials()
        self.create_livros()

    def post_colecao(self, data):
        url = reverse("colecao-list")
        response = self.client.post(url, data, format="json")
        return response

    def test_create_collection_auth(self):
        data = {
            "nome": "nome",
            "descricao": "descricao",
            "livros": [self.livro1.pk],
            "colecionador": self.user2.pk,
        }
        print(data)
        token = Token.objects.create(user=self.user2)
        self.client.credentials(HTTP_AUTHORIZATION="Token {0}".format(token.key))
        response = self.post_colecao(data,)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(1, Colecao.objects.count())
        self.assertEqual(response.data["nome"], Colecao.objects.get().nome)
        self.assertEqual(response.data["descricao"], Colecao.objects.get().descricao)
        self.assertEqual(response.data["livros"],
            list(Colecao.objects.get().livros.values_list("pk", flat=True)),
        )
        self.assertEqual(response.data["colecionador"], Colecao.objects.get().colecionador.pk)

    def test_edit_user_collection(self):
        self.client.login(username="user1", password="password1")
        colecao = Colecao.objects.create(nome="Minha Coleção", descricao="Descrição", colecionador=self.user1)
        self.client.login(username="user2", password="password2")
        data = {"nome": "Nova Coleção"}
        url = f"{self.colecoes_url}{colecao.id}/"
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.login(username="user1", password="password1")
        data = {"nome": "Coleção Editada"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nome"], "Coleção Editada")

    def test_create_collection_no_auth(self):
        data = {
            "nome": "nome",
            "descricao": "descricao",
            "livros": [self.livro1.pk],
            "colecionador": self.user2.pk,
        }
        # self.client.login(username="user1", password="password1")
        response = self.post_colecao(data,)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(1, Colecao.objects.count())
        self.assertEqual(response.data["nome"], Colecao.objects.get().nome)
        self.assertEqual(response.data["descricao"], Colecao.objects.get().descricao)
        self.assertEqual(response.data["livros"],
            list(Colecao.objects.get().livros.values_list("pk", flat=True)),
        )
        self.assertEqual(response.data["colecionador"], Colecao.objects.get().colecionador.pk)
