from django import forms
from .models import task


class taskForm(forms.ModelForm):
    class Meta:
        model = task
        fields = ['titulo', 'description', 'importante']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Escribir titulo'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escribir Descripcion'}),
            'importante': forms.CheckboxInput(attrs={'class': 'form-check-input m-auto'}),
        }
