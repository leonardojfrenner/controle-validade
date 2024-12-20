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
import os

def register(request):
    if request.method == 'POST':
        form = FarmaciaRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, 'Conta criada com sucesso! Faça login para continuar.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Erro ao criar conta: {str(e)}')
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f'{field.label}: {error}')
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
    produtos_ids = request.POST.getlist('produtos_selecionados')
    
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
        dias_restantes = (produto.data_validade - timezone.now().date()).days
        data.append({
            'Código': str(produto.codigo_barras),  # Convertendo para string
            'Descrição': str(produto.descricao),
            'Categoria': str(produto.categoria),
            'Data de Validade': produto.data_validade.strftime('%d/%m/%Y'),  # Formatando data
            'Quantidade': str(produto.quantidade),
            'Lote': str(produto.lote),
            'Dias Restantes': dias_restantes
        })
    
    df = pd.DataFrame(data)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_arquivo = f'produtos_{slugify(request.user.nome_loja)}_{timestamp}.xlsx'
    
    with pd.ExcelWriter(nome_arquivo, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Produtos')
        
        workbook = writer.book
        worksheet = writer.sheets['Produtos']
        
        # Formato para cabeçalho
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'bg_color': '#D9D9D9',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })
        
        # Formato para células normais
        cell_format = workbook.add_format({
            'font_size': 10,
            'border': 1,
            'align': 'left',
            'valign': 'vcenter'
        })
        
        # Formato para números
        number_format = workbook.add_format({
            'font_size': 10,
            'border': 1,
            'align': 'right',
            'valign': 'vcenter'
        })
        
        # Definir larguras específicas para cada coluna
        column_widths = {
            'Código': 15,
            'Descrição': 30,
            'Categoria': 15,
            'Data de Validade': 15,
            'Quantidade': 12,
            'Lote': 12,
            'Dias Restantes': 12
        }
        
        # Aplicar formatos e larguras
        for col_num, (col_name, width) in enumerate(column_widths.items()):
            worksheet.set_column(col_num, col_num, width)
            worksheet.write(0, col_num, col_name, header_format)
            
            # Aplicar formato específico para cada coluna
            if col_name in ['Código', 'Dias Restantes', 'Quantidade']:
                for row_num in range(len(df)):
                    worksheet.write(row_num + 1, col_num, df.iloc[row_num][col_name], number_format)
            else:
                for row_num in range(len(df)):
                    worksheet.write(row_num + 1, col_num, df.iloc[row_num][col_name], cell_format)
    
    # Ler e retornar o arquivo
    with open(nome_arquivo, 'rb') as file:
        response = HttpResponse(
            file.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
    
    os.remove(nome_arquivo)
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

@login_required
def ajuda(request):
    return render(request, 'core/ajuda.html')
