from django import forms
from django.contrib import admin
from .models import Factura, Usuario, Contrato, Administrador

# Vista Admin para Usuario
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ["id", "correo", "nombre", "apellido", "clave", "rol"] 

# Formulario para el modelo Contrato
class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ['usuario','servicio', 'fecha', 'nombres', 'apellidos', 'cedula', 'direccion', 'detalles', 'obligaciones', 'duracion', 'precio', 'confidencialidad' , 'pagado']

class FacturasAdmin(admin.ModelAdmin):
    list_display = ['contrato' , 'mes' , 'anio' , 'pagado']


# Vista Admin para Contrato
class ContratoAdmin(admin.ModelAdmin):
    form = ContratoForm  
    list_display = ['usuario__nombre','usuario', 'servicio', 'fecha', 'nombres', 'apellidos', 'cedula', 'direccion', 'duracion', 'precio', 'estado_contrato']

    def estado_contrato(self, obj):
        return obj.estado_contrato
    estado_contrato.short_description = 'Estado del Contrato'


# Registrar modelos en el Admin
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Contrato, ContratoAdmin) 
admin.site.register(Factura, FacturasAdmin) 

class AdministradorAdmin(admin.ModelAdmin):
    list_display = ["id", "codigo_ini", "contraseña"] 

admin.site.register(Administrador, AdministradorAdmin)