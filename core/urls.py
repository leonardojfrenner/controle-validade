from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('', views.dashboard, name='dashboard'),
    path('produto/novo/', views.produto_novo, name='produto_novo'),
    path('produto/<int:pk>/editar/', views.produto_editar, name='produto_editar'),
    path('produto/<int:pk>/excluir/', views.produto_excluir, name='produto_excluir'),
    path('exportar-excel/', views.exportar_excel, name='exportar_excel'),
    path('consultar-produto/', views.consultar_produto, name='consultar_produto'),
    path('produto/<int:pk>/detalhes/', views.produto_detalhes, name='produto_detalhes'),
    path('confirmar-retirada/', views.confirmar_retirada, name='confirmar_retirada'),
    path('historico/', views.historico, name='historico'),
    path('ajuda/', views.ajuda, name='ajuda'),
] 