from django import forms
from .models import Artista

class UserRegistrationForm(forms.ModelForm):
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar Contraseña'})
    )
    ncontacto = forms.CharField(
        label='Número de Contacto', 
        max_length=15, 
        required=True,  
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu número de contacto'})
    )
    imagen = forms.ImageField(
        label='Foto de Perfil',
        required=True,  
        widget=forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'image/*'})
    )

    class Meta:
        model = Artista
        fields = ['usuario', 'correo', 'contrasenia', 'password2', 'ncontacto', 'imagen']
        widgets = {
            'usuario': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ingresa un usuario'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Tu correo electronico'}),
            'contrasenia': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ingresar contraseña'})
        }
        labels = {
            'usuario': 'Nombre de Usuario',
            'correo': 'Correo Electrónico',
            'contrasenia': 'Contraseña'
        }

    def clean(self):
        cleaned_data = super().clean()
        contrasenia = cleaned_data.get("contrasenia")
        password2 = cleaned_data.get("password2")

        if contrasenia and password2 and contrasenia != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return cleaned_data