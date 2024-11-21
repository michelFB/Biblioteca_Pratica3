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

    # def create_user_and_set_token_credentials(self):
    #     self.user = User.objects.create_user(
    #         "user01", "user01@example.com", "user01P4ssw0rD"
    #     )
    #     token = Token.objects.create(user=self.user)
    #     self.client.credentials(HTTP_AUTHORIZATION="Token {0}".format(token.key))

    # def create_livro(self):
    #     autor = Autor.objects.create(name="J.R.R. Tolkien")
    #     categoria = Categoria.objects.create(nome="Fantasia")
    #     self.livro = Livro.objects.create(
    #         titulo = "oSenhor dos aneis",
    #         autor = autor,
    #         categoria = categoria,
    #         publicado_em = "1954-07-29",
    #     )

    # def setUp(self):
    #     self.create_user_and_set_token_credentials()
    #     self.create_livro()

    # def post_colecao(self, nome, descricao, livros, colecionador):
    #     url = reverse("colecao-list")
    #     data = {
    #         "nome": nome,
    #         "descricao": descricao,
    #         "livros": livros,
    #         "colecionador": colecionador,
    #     }
    #     response = self.client.post(url, data, format="json")
    #     return response

    # def test_get_colecao(self):
    #     new_colecao_nome = "raro Demais"
    #     new_colecao_descricao = "Os melhores de 90"
    #     new_colecao_livros = [self.livro.pk]
    #     new_colecao_colecionador = self.user.pk
    #     response = self.post_colecao(
    #         new_colecao_nome,
    #         new_colecao_descricao,
    #         new_colecao_livros,
    #         new_colecao_colecionador,
    #     )
    #     self.assertEqual(status.HTTP_201_CREATED, response.status_code)
    #     self.assertEqual(1, Colecao.objects.count())
    #     self.assertEqual(new_colecao_nome, Colecao.objects.get().nome)
    #     self.assertEqual(new_colecao_descricao, Colecao.objects.get().descricao)
    #     self.assertEqual(new_colecao_livros, 
    #                      list(Colecao.objects.get().livros.values_list("pk", flat=True)))
    #     self.assertEqual(new_colecao_colecionador, Colecao.objects.get().colecionador.pk)

    def setUp(self):

        self.user1 = User.objects.create_user(username="user1", password="password1")
        self.user2 = User.objects.create_user(username="user2", password="password2")

        self.categoria = Categoria.objects.create(nome="Categoria 1")
        self.autor = Autor.objects.create(nome="Autor 1")

        self.livro1 = Livro.objects.create(
            titulo="Livro 1", autor=self.autor, categoria=self.categoria, publicado_em="2023-01-01"
        )
        self.livro2 = Livro.objects.create(
            titulo="Livro 2", autor=self.autor, categoria=self.categoria, publicado_em="2023-01-01"
        )

        self.colecoes_url = "/api/colecoes/"

    def test_create_collection_auth(self):

        self.client.login(username="user1", password="password1")
        data = {
            "nome": "Minha Coleção",
            "descricao": "Descrição da coleção",
            "livros": [self.livro1.id, self.livro2.id],
        }
        response = self.client.post(self.colecoes_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["colecionador"], "user1")
        self.assertEqual(response.data["nome"], "Minha Coleção")

    def test_create_collection(self):
     
        data = {
            "nome": "Coleção Pública",
            "descricao": "Tentativa de criação sem autenticação",
            "livros": [self.livro1.id]
        }
        response = self.client.post(self.colecoes_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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

    def test_delete_user_collection(self):

        self.client.login(username="user1", password="password1")
        colecao = Colecao.objects.create(nome="Minha Coleção", descricao="Descrição", colecionador=self.user1)
        
        self.client.login(username="user2", password="password2")
        url = f"{self.colecoes_url}{colecao.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.login(username="user1", password="password1")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Colecao.objects.filter(id=colecao.id).exists())

    def test_list_collections_auth(self):
        Colecao.objects.create(nome="Coleção 1", descricao="Descrição 1", colecionador=self.user1)
        Colecao.objects.create(nome="Coleção 2", descricao="Descrição 2", colecionador=self.user2)

        self.client.login(username="user1", password="password1")
        response = self.client.get(self.colecoes_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)  # Deve incluir coleções de outros usuários

        response_data = response.data["results"]
        self.assertEqual(response_data[0]["nome"], "Coleção 1")
        self.assertEqual(response_data[1]["nome"], "Coleção 2")

    def test_list_collections(self):
 
        response = self.client.get(self.colecoes_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_collection_invalid_data(self):
        self.client.login(username="user1", password="password1")

        data = {"descricao": "Sem nome", "livros": [self.livro1.id]}
        response = self.client.post(self.colecoes_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {"nome": "Coleção Inválida", "descricao": "Livro inexistente", "livros": [9999]}
        response = self.client.post(self.colecoes_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {"nome": "Coleção Inválida", "descricao": "Sem livros", "livros": []}
        response = self.client.post(self.colecoes_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_database_persistence(self):
        self.client.login(username="user1", password="password1")
        data = {"nome": "Coleção Persistida", "descricao": "Teste", "livros": [self.livro1.id]}
        self.client.post(self.colecoes_url, data)

        colecao = Colecao.objects.get(nome="Coleção Persistida")
        self.assertEqual(colecao.descricao, "Teste")
        self.assertEqual(colecao.colecionador, self.user1)
        self.assertIn(self.livro1, colecao.livros.all())

    def test_user_can_access_other_collections(self):
        colecao = Colecao.objects.create(nome="Coleção Pública", descricao="Teste", colecionador=self.user2)

        self.client.login(username="user1", password="password1")
        url = f"{self.colecoes_url}{colecao.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nome"], "Coleção Pública")
        self.assertEqual(response.data["colecionador"], "user2")

    def test_view_other_user_collection(self):
        colecao = Colecao.objects.create(nome="Coleção Pública", descricao="Visível", colecionador=self.user2)

        self.client.login(username="user1", password="password1")
        url = f"{self.colecoes_url}{colecao.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nome"], "Coleção Pública")
        self.assertEqual(response.data["descricao"], "Visível")
        self.assertEqual(response.data["colecionador"], "user2")

    def test_edit_other_user_collection_forbidden(self):
        colecao = Colecao.objects.create(nome="Coleção Pública", descricao="Visível", colecionador=self.user2)

        self.client.login(username="user1", password="password1")
        url = f"{self.colecoes_url}{colecao.id}/"
        data = {"nome": "Tentativa de Edição"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_other_user_collection_forbidden(self):
        colecao = Colecao.objects.create(nome="Coleção Pública", descricao="Visível", colecionador=self.user2)

        self.client.login(username="user1", password="password1")
        url = f"{self.colecoes_url}{colecao.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_model_str_methods(self):
        colecao = Colecao.objects.create(nome="Minha Coleção", descricao="Teste", colecionador=self.user1)
        self.assertEqual(str(colecao), "Minha Coleção - user1")

    def test_urls_resolve(self):
        from django.urls import reverse, resolve
        resolver = resolve(reverse("livros-list"))
        self.assertEqual(resolver.view_name, "livros-list")

    def test_autor_str(self):
        autor = Autor.objects.create(nome="Autor Teste")
        self.assertEqual(str(autor), "Autor Teste")

    def test_categoria_str(self):
        categoria = Categoria.objects.create(nome="Categoria Teste")
        self.assertEqual(str(categoria), "Categoria Teste")

    def test_colecao_str(self):
        colecao = Colecao.objects.create(
            nome="Minha Coleção",
            descricao="Descrição Teste",
            colecionador=self.user1
        )
        self.assertEqual(str(colecao), "Minha Coleção - user1")

    def test_livro_str(self):
        livro = Livro.objects.create(
            titulo="Livro Teste",
            autor=self.autor,
            categoria=self.categoria,
            publicado_em="2023-01-01"
        )
        self.assertEqual(str(livro), "Livro Teste")
