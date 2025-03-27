from django.db import models

class Usuario(models.Model):
        correo = models.EmailField(max_length=254, unique = True)
        id = models.AutoField(primary_key=True)
        nombre = models.CharField(max_length=100)
        apellido = models.CharField(max_length=100)
        clave = models.CharField(max_length=254)
        ROLES =(
                ('U', "Usuario"),
        )
        rol = models.CharField(max_length=1, choices=ROLES, default='U')

class Contrato(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)        
    SERVICIO_CHOICES = [
        ('agua', 'Agua'),
        ('luz', 'Luz'),
        ('gas', 'Gas'),
        ('telefonia', 'Telefonía'),
        ('internet', 'Internet'),
    ]
    servicio = models.CharField(max_length=50, choices=SERVICIO_CHOICES)
    fecha = models.DateField()
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20)
    direccion = models.CharField(max_length=200)
    detalles = models.TextField(blank=True, null=True)
    duracion = models.PositiveIntegerField()  # Duración en meses
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    confidencialidad = models.BooleanField(default=False)
    obligaciones = models.TextField(blank=True)        
    pagado = models.BooleanField(default=False)
    def __str__(self):
        return f"Contrato de {self.nombres} {self.apellidos} para {self.servicio}"
# Propiedad para verificar si todas las facturas están pagadas
    @property
    def estado_contrato(self):
        if self.factura_set.filter(pagado=False).exists():
            return "Pendiente"
        else:
            return "Pagado"
    
class Factura(models.Model):
        contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE)
        mes = models.PositiveIntegerField()  # Mes del contrato (1-12)
        anio = models.PositiveIntegerField()  # Año del contrato
        monto = models.DecimalField(max_digits=10, decimal_places=2)
        pagado = models.BooleanField(default=False)  # Indica si la factura fue pagada

        def __str__(self):
                return f"Factura {self.id} - Contrato: {self.contrato.id} - Mes: {self.mes}/{self.anio}"
        

class Administrador(models.Model):
        codigo_ini = models.CharField(max_length=15)
        contraseña = models.CharField(max_length=20)

        def __str__(self):
                return self.codigo_ini