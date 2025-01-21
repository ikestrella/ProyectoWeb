from django import forms
from .models import Artista

class UserRegistrationForm(forms.ModelForm):
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar Contraseña'})
    )

    class Meta:
        model = Artista
        fields = ['usuario', 'contrasenia', 'password2', 'correo']
        widgets = {
            'usuario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa un usuario'}),
            'contrasenia': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ingresar contraseña'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Tu correo electrónico (opcional)'})
        }
        labels = {
            'usuario': 'Nombre de Usuario',
            'contrasenia': 'Contraseña',
            'correo': 'Correo Electrónico'
        }

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['correo'].required = False

    def clean(self):
        cleaned_data = super().clean()
        contrasenia = cleaned_data.get("contrasenia")
        password2 = cleaned_data.get("password2")

        if contrasenia and password2 and contrasenia != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return cleaned_data