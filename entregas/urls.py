from django.urls import path

from . import views

urlpatterns = [
    path("cadastro/", views.CadastroEmpresaView.as_view(), name="cadastro"),
    path("login/", views.EmpresaLoginView.as_view(), name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/analises/", views.analytics, name="analytics"),
    path("entregas/nova/", views.criar_entrega, name="criar_entrega"),
    path("entregas/<str:codigo>/", views.detalhe_entrega, name="detalhe_entrega"),
    path("rastreio/", views.RastreioPublicoView.as_view(), name="rastreio"),
    path("rastreio/<str:codigo>/", views.RastreioPublicoView.as_view(), name="rastreio_codigo"),
    path("api/rastreio/<str:codigo>/", views.RastreioPublicoAPIView.as_view(), name="api_rastreio"),
]
