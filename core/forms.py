from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Farmacia
import re

class FarmaciaRegistrationForm(UserCreationForm):
    cpf = forms.CharField(
        label='CPF',
        max_length=14,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'})
    )
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'})
    )
    nome_loja = forms.CharField(
        label='Nome da Farmácia',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Farmacia
        fields = ('username', 'nome_loja', 'cpf', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Remove caracteres não numéricos
            cpf = re.sub(r'[^0-9]', '', cpf)
            
            # Verifica se tem 11 dígitos
            if len(cpf) != 11:
                raise forms.ValidationError('CPF deve conter 11 dígitos.')
            
            # Formata o CPF
            cpf = f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
            
            # Verifica se o CPF já existe
            if Farmacia.objects.filter(cpf=cpf).exists():
                raise forms.ValidationError('Este CPF já está cadastrado.')
            
        return cpf

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Farmacia.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email já está cadastrado.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.nome_loja = self.cleaned_data['nome_loja']
        if commit:
            user.save()
        return user 