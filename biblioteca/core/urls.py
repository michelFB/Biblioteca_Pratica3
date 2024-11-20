from django.urls import path, include
from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r"colecao", views.ColecaoViewSet)

urlpatterns = [
    path('livros/', views.LivroList.as_view(), name=views.LivroList.name),
    path('livros/<int:pk>/', views.LivroDetail.as_view(), name=views.LivroDetail.name),
    path('autores/', views.AutorList.as_view(), name=views.AutorList.name),
    path('autores/<int:pk>/', views.AutorDetail.as_view(), name=views.AutorDetail.name),
    path('categorias/', views.CategoriaList.as_view(), name=views.CategoriaList.name),
    path('categorias/<int:pk>/', views.CategoriaDetail.as_view(), name=views.CategoriaDetail.name),
    # path('colecao/', views.ColecaoListCreate.as_view(), name=views.ColecaoListCreate.name),
    # path('colecao/<int:pk>/', views.ColecaoDetail.as_view(), name=views.ColecaoDetail.name),
    path('', views.ApiRoot.as_view(), name=views.ApiRoot.name),
]
urlpatterns += router.urls
