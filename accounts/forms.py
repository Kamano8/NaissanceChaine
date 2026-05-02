# ============================================================
# NaissanceChain — Formulaires d'authentification
# ============================================================

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Utilisateur, RoleChoices, RegionGuinee


class FormulaireConnexion(AuthenticationForm):
    """
    Formulaire de connexion personnalisé.
    Champ username remplacé par email.
    """
    username = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={
            'class':       'form-control form-control-lg',
            'placeholder': 'votre@email.com',
            'autofocus':   True,
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class':       'form-control form-control-lg',
            'placeholder': '••••••••',
        })
    )

    error_messages = {
        'invalid_login': "Email ou mot de passe incorrect. Veuillez réessayer.",
        'inactive':      "Ce compte est désactivé. Contactez l'administrateur.",
    }


class FormulaireModificationProfil(forms.ModelForm):
    """
    Formulaire de modification du profil utilisateur connecté.
    """
    class Meta:
        model  = Utilisateur
        fields = ['nom', 'prenom', 'telephone', 'region', 'prefecture', 'photo']
        widgets = {
            'nom':        forms.TextInput(attrs={'class': 'form-control'}),
            'prenom':     forms.TextInput(attrs={'class': 'form-control'}),
            'telephone':  forms.TextInput(attrs={'class': 'form-control'}),
            'region':     forms.Select(attrs={'class': 'form-select'}),
            'prefecture': forms.TextInput(attrs={'class': 'form-control'}),
            'photo':      forms.FileInput(attrs={'class': 'form-control'}),
        }


class FormulaireInscriptionCitoyen(forms.ModelForm):
    """
    Formulaire d'auto-inscription pour les citoyens (familles).
    Le rôle est forcé à CITOYEN.
    """
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': '••••••••'})
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': '••••••••'})
    )

    class Meta:
        model  = Utilisateur
        fields = ['email', 'nom', 'prenom', 'telephone']
        widgets = {
            'email':     forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'votre@email.com'}),
            'nom':       forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Votre nom'}),
            'prenom':    forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Votre prénom'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': '+224 6XX XXX XXX'}),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return p2

    def save(self, commit=True):
        utilisateur = super().save(commit=False)
        utilisateur.set_password(self.cleaned_data['password1'])
        utilisateur.role = RoleChoices.CITOYEN
        if commit:
            utilisateur.save()
        return utilisateur


class FormulaireCreationUtilisateur(forms.ModelForm):
    """
    Formulaire de création d'un utilisateur (admin seulement).
    """
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model  = Utilisateur
        fields = ['email', 'nom', 'prenom', 'telephone', 'role', 'region', 'prefecture', 'photo']
        widgets = {
            'email':       forms.EmailInput(attrs={'class': 'form-control'}),
            'nom':         forms.TextInput(attrs={'class': 'form-control'}),
            'prenom':      forms.TextInput(attrs={'class': 'form-control'}),
            'telephone':   forms.TextInput(attrs={'class': 'form-control'}),
            'role':        forms.Select(attrs={'class': 'form-select'}),
            'region':      forms.Select(attrs={'class': 'form-select'}),
            'prefecture':  forms.TextInput(attrs={'class': 'form-control'}),
            'photo':       forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        """Vérifie que les deux mots de passe correspondent"""
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return p2

    def save(self, commit=True):
        """Sauvegarde l'utilisateur avec le mot de passe haché"""
        utilisateur = super().save(commit=False)
        utilisateur.set_password(self.cleaned_data['password1'])
        if commit:
            utilisateur.save()
        return utilisateur