from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Farmacia

class FarmaciaCreationForm(UserCreationForm):
    nome_loja = forms.CharField(
        label='Nome da Farmácia',
        max_length=100,
        help_text='Digite o nome da sua farmácia'
    )
    username = forms.CharField(
        label='Usuário',
        help_text='Obrigatório. 150 caracteres ou menos. Letras, números e @/./+/-/_ apenas.'
    )
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput,
        help_text='Sua senha deve conter pelo menos 8 caracteres.'
    )
    password2 = forms.CharField(
        label='Confirme a senha',
        widget=forms.PasswordInput,
        help_text='Digite a mesma senha novamente.'
    )

    class Meta:
        model = Farmacia
        fields = ('username', 'nome_loja', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.nome_loja = self.cleaned_data['nome_loja']
        if commit:
            user.save()
        return user 