# ============================================================
# NaissanceChain — Formulaires de l'app Agents
# ============================================================

from django import forms
from .models import Agent, StatutAgent


class FormulairePositionGPS(forms.Form):
    """Formulaire de mise à jour manuelle de la position GPS"""
    latitude  = forms.DecimalField(
        max_digits=10, decimal_places=7,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0000001'})
    )
    longitude = forms.DecimalField(
        max_digits=10, decimal_places=7,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0000001'})
    )
    precision = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )


class FormulaireCreationAgent(forms.ModelForm):
    """Formulaire de création / modification d'un agent (admin)"""

    class Meta:
        model  = Agent
        fields = [
            'code_agent', 'secteur', 'centre_etat_civil',
            'statut', 'objectif_hebdomadaire'
        ]
        widgets = {
            'code_agent':          forms.TextInput(attrs={'class': 'form-control'}),
            'secteur':             forms.TextInput(attrs={'class': 'form-control'}),
            'centre_etat_civil':   forms.TextInput(attrs={'class': 'form-control'}),
            'statut':              forms.Select(attrs={'class': 'form-select'}),
            'objectif_hebdomadaire': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'code_agent':            'Code agent',
            'secteur':               'Secteur d\'intervention',
            'centre_etat_civil':     'Centre d\'état civil',
            'statut':                'Statut',
            'objectif_hebdomadaire': 'Objectif hebdomadaire (actes)',
        }