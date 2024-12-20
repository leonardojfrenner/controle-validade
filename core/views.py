from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import FarmaciaRegistrationForm
from .models import Farmacia, Produto
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
import pandas as pd
from django.http import HttpResponse, JsonResponse
from django.utils.text import slugify
from datetime import datetime
import requests

def register(request):
    if request.method == 'POST':
        form = FarmaciaRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = FarmaciaRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def dashboard(request):
    categoria_filtro = request.GET.get('categoria', '')
    status_filtro = request.GET.get('status', 'ATIVO')
    
    produtos = Produto.objects.filter(farmacia=request.user)
    
    if categoria_filtro:
        produtos = produtos.filter(categoria=categoria_filtro)
    if status_filtro:
        produtos = produtos.filter(status=status_filtro)
    
    produtos_vencendo = produtos.filter(
        status='ATIVO',
        data_validade__lte=timezone.now().date() + timedelta(days=15)
    ).order_by('data_validade')
    
    context = {
        'produtos': produtos.order_by('data_validade'),
        'produtos_vencendo': produtos_vencendo,
        'categoria_selecionada': categoria_filtro,
        'total_medicamentos': produtos.filter(categoria='MEDICAMENTO', status='ATIVO').count(),
        'total_controlados': produtos.filter(categoria='CONTROLADO', status='ATIVO').count(),
        'total_termolabeis': produtos.filter(categoria='TERMOLABEL', status='ATIVO').count(),
        'total_alimentos': produtos.filter(categoria='ALIMENTO', status='ATIVO').count(),
        'total_perfumaria': produtos.filter(categoria='PERFUMARIA', status='ATIVO').count(),
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def produto_novo(request):
    if request.method == 'POST':
        codigo_barras = request.POST.get('codigo_barras')
        descricao = request.POST.get('descricao')
        categoria = request.POST.get('categoria')
        data_validade = request.POST.get('data_validade')
        quantidade = request.POST.get('quantidade')
        lote = request.POST.get('lote')
        
        Produto.objects.create(
            farmacia=request.user,
            codigo_barras=codigo_barras,
            descricao=descricao,
            categoria=categoria,
            data_validade=data_validade,
            quantidade=quantidade,
            lote=lote
        )
        messages.success(request, 'Produto cadastrado com sucesso!')
        return redirect('dashboard')
    
    return render(request, 'core/produto_form.html')

@login_required
def produto_editar(request, pk):
    produto = get_object_or_404(Produto, pk=pk, farmacia=request.user)
    
    if request.method == 'POST':
        produto.codigo_barras = request.POST.get('codigo_barras')
        produto.descricao = request.POST.get('descricao')
        produto.data_validade = request.POST.get('data_validade')
        produto.quantidade = request.POST.get('quantidade')
        produto.lote = request.POST.get('lote')
        produto.save()
        
        messages.success(request, 'Produto atualizado com sucesso!')
        return redirect('dashboard')
    
    return render(request, 'core/produto_form.html', {'produto': produto})

@login_required
def produto_excluir(request, pk):
    produto = get_object_or_404(Produto, pk=pk, farmacia=request.user)
    produto.delete()
    messages.success(request, 'Produto excluído com sucesso!')
    return redirect('dashboard')

@login_required
def exportar_excel(request):
    # Obtém os IDs dos produtos selecionados
    produtos_ids = request.POST.getlist('produtos_selecionados')
    
    # Se houver produtos selecionados, filtra apenas eles
    if produtos_ids:
        produtos = Produto.objects.filter(
            farmacia=request.user,
            id__in=produtos_ids
        )
    else:
        produtos = Produto.objects.filter(farmacia=request.user)
    
    # Cria DataFrame com os dados
    data = []
    for produto in produtos:
        data.append({
            'Código de Barras': produto.codigo_barras,
            'Descrição': produto.descricao,
            'Data de Validade': produto.data_validade,
            'Quantidade': produto.quantidade,
            'Lote': produto.lote,
            'Status': 'Próximo ao vencimento' if produto.proximo_vencimento else 'Normal'
        })
    
    df = pd.DataFrame(data)
    
    # Cria o arquivo Excel
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_arquivo = f'produtos_{slugify(request.user.nome_loja)}_{timestamp}.xlsx'
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
    
    # Salva o DataFrame como Excel
    df.to_excel(response, index=False, engine='openpyxl')
    
    return response

def consultar_produto(request):
    codigo_barras = request.GET.get('codigo_barras')
    
    try:
        # Busca o produto mais recente com o mesmo código de barras
        produto = Produto.objects.filter(
            codigo_barras=codigo_barras,
            farmacia=request.user
        ).latest('data_cadastro')
        
        return JsonResponse({
            'success': True,
            'descricao': produto.descricao,
            'encontrado': True,
            'message': 'Produto encontrado no histórico'
        })
    except Produto.DoesNotExist:
        return JsonResponse({
            'success': True,
            'encontrado': False,
            'message': 'Novo produto - preencha a descrição'
        })

@login_required
def produto_detalhes(request, pk):
    produto = get_object_or_404(Produto, pk=pk, farmacia=request.user)
    return render(request, 'core/produto_detalhes.html', {'produto': produto})

@login_required
def confirmar_retirada(request):
    if request.method == 'POST':
        produtos_selecionados = request.POST.getlist('produtos_selecionados')
        motivo = request.POST.get('motivo', '')
        
        if produtos_selecionados and motivo:
            produtos = Produto.objects.filter(
                id__in=produtos_selecionados,
                farmacia=request.user
            )
            
            for produto in produtos:
                produto.status = 'RETIRADO'
                produto.motivo_retirada = motivo
                produto.data_retirada = timezone.now()
                produto.save()
            
            messages.success(request, 'Produtos retirados com sucesso!')
        else:
            messages.error(request, 'Selecione produtos e informe o motivo da retirada.')
            
    return redirect('dashboard')

@login_required
def historico(request):
    data_limite = timezone.now() - timedelta(days=90)
    produtos_retirados = Produto.objects.filter(
        farmacia=request.user,
        status='RETIRADO',
        data_retirada__gte=data_limite
    ).order_by('-data_retirada')
    
    return render(request, 'core/historico.html', {'produtos': produtos_retirados})
