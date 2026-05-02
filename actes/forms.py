from django import forms
from .models import ActeNaissance

class NaissanceForm(forms.ModelForm):

    class Meta:
        model = ActeNaissance
        fields = [
            'nom_enfant',
            'prenoms_enfant',
            'date_naissance',
            'lieu_naissance',
            'sexe',
            'nom_mere',
            'nom_pere',
            'poids',
            'taille'
        ]

        widgets = {
            'nom_enfant': forms.TextInput(attrs={'class': 'form-control'}),
            'prenoms_enfant': forms.TextInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'lieu_naissance': forms.TextInput(attrs={'class': 'form-control'}),
            'sexe': forms.Select(attrs={'class': 'form-control'}),
            'nom_mere': forms.TextInput(attrs={'class': 'form-control'}),
            'nom_pere': forms.TextInput(attrs={'class': 'form-control'}),
            'poids': forms.NumberInput(attrs={'class': 'form-control'}),
            'taille': forms.NumberInput(attrs={'class': 'form-control'}),
        }