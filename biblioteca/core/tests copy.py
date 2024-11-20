from django.utils.http import urlencode
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Colecao, Autor
from core import views
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import pytest


class ColecaoTests(APITestCase):

    def post_colecao(self, nome, descricao, livros, colecionador, owner):
        url = reverse("colecao-list")
        print(url)
        data = {
            "nome": nome,
            "descricao": descricao,
            "livros": livros,
            "colecionador": colecionador,
            "owner": owner,
        }
        response = self.client.post(url, data, format="json")
        return response

    def create_user_and_set_token_credentials(self):
        user = User.objects.create_user(
            "user01", "user01@example.com", "user01P4ssw0rD"
        )
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION="Token {0}".format(token.key))

    def user(db): 
        return User.objects.create_user(username='colecionador', password='password') 

    def another_user(db): 
        return User.objects.create_user(username='owner', password='password')

    def setUp(self):
        self.create_user_and_set_token_credentials()
        self.colecao = Colecao.objects.create(
            nome="Raridades",
            descricao="Melhores",
            livros=[2],
            colecionador= user,  
            # Aqui passamos a instância de User 
            owner= another_user
        )

    def test_get_colecao(self):
        url = reverse(views.ColecaoDetail.name, None, {self.Colecao.pk})
        authorized_get_response = self.client.get(url, format="json")
        self.assertEqual(status.HTTP_200_OK, authorized_get_response.status_code)
        self.assertEqual(self.Colecao.name, authorized_get_response.data["nome"])

    #      def post_autores(self, name):
    #         url = reverse("autor-list")
    #         data = {"name": name}
    #         response = self.client.post(url, data, format="json")
    #         return response

    #     # Testa o método POST
    #      def test_post_and_get_autores(self):
    #         new_autores_name = "autoresRara10"
    #         response = self.post_autores(new_autores_name)
    #         print("PK {0}".format(Autor.objects.get().pk))
    #         self.assertEqual(status.HTTP_201_CREATED, response.status_code)
    #         self.assertEqual(1, Autor.objects.count())
    #         self.assertEqual(new_autores_name, Autor.objects.get().name)

    # def create_user_and_set_token_credentials(self):
    #    user = User.objects.create_user(
    #        "user01", "user01@example.com", "user01Password"
    #    )
    #    token = Token.objects.create(user=user)
    #    self.client.credentials(HTTP_AUTHORIZATION="Token {0}".format(token.key))

    # def setUp(self):
    #    self.create_user_and_set_token_credentials()
    #    self.colecao = Colecao.objects.create(
    #        nome="COLECAO_TEST",descricao="TESTE",livros=[8],
    #        colecionador=1,owner="user01")

    # def post_colecao(self, data):
    #     url = reverse("colecao-list")
    #     response = self.client.post(url, data, format="json")
    #     return response

    # # Testa o método POST
    # def test_post_and_get_colecao(self):
    #     new_colecao_name = {
    #         "nome": "COLECAO_TEST",
    #         "descricao": "TESTE",
    #         "livros": [8],
    #         "colecionador": 1,
    #         "owner": "user01",
    #     }
    #     response = self.post_colecao(new_colecao_name)
    #     print("PK {0}".format(Colecao.objects.get().pk))
    # print("PK {0}".format(Colecao.objects.get().pk))
    # self.assertEqual(status.HTTP_201_CREATED, response.status_code)
    # self.assertEqual(1, Colecao.objects.count())
    # self.assertEqual(new_colecao_name, Colecao.objects.get().name)
