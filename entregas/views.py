from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView
from rest_framework.generics import RetrieveAPIView

from .analytics import calcular_metricas
from .forms import CadastroEmpresaForm, EntregaForm, StatusHistoricoForm
from .models import Entrega
from .serializers import EntregaPublicaSerializer


class CadastroEmpresaView(CreateView):
    form_class = CadastroEmpresaForm
    template_name = "entregas/cadastro.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class EmpresaLoginView(LoginView):
    template_name = "entregas/login.html"


@login_required
def dashboard(request):
    entregas = request.user.empresa.entregas.all()
    return render(request, "entregas/dashboard.html", {"entregas": entregas})


@login_required
def criar_entrega(request):
    if request.method == "POST":
        form = EntregaForm(request.POST)
        if form.is_valid():
            entrega = form.save(commit=False)
            entrega.empresa = request.user.empresa
            entrega.save()
            return redirect("detalhe_entrega", codigo=entrega.codigo_rastreio)
    else:
        form = EntregaForm()
    return render(request, "entregas/criar_entrega.html", {"form": form})


@login_required
def detalhe_entrega(request, codigo):
    entrega = get_object_or_404(Entrega, codigo_rastreio=codigo, empresa=request.user.empresa)

    if request.method == "POST":
        form = StatusHistoricoForm(request.POST, request.FILES, entrega=entrega)
        if form.is_valid():
            novo_status = form.save(commit=False)
            novo_status.entrega = entrega
            novo_status.save()
            return redirect("detalhe_entrega", codigo=entrega.codigo_rastreio)
    else:
        form = StatusHistoricoForm(entrega=entrega)

    return render(
        request,
        "entregas/detalhe_entrega.html",
        {"entrega": entrega, "form": form, "historico": entrega.historico.all()},
    )


@login_required
def analytics(request):
    metricas = calcular_metricas(request.user.empresa)
    return render(request, "entregas/analytics.html", {"metricas": metricas})


class RastreioPublicoView(TemplateView):
    """Página pública. O carregamento dos dados é feito via JavaScript
    consumindo a API (/api/rastreio/<codigo>/), sem necessidade de reload."""

    template_name = "entregas/rastreio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["codigo"] = kwargs.get("codigo", "")
        return context


class RastreioPublicoAPIView(RetrieveAPIView):
    serializer_class = EntregaPublicaSerializer
    lookup_field = "codigo_rastreio"
    lookup_url_kwarg = "codigo"
    queryset = Entrega.objects.all()
