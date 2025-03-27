from datetime import timedelta
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from dateutil.relativedelta import relativedelta  # Asegúrate de tener esta línea

from .admin import ContratoForm
from .models import * #Importa todo lo que haya en el modelo (mas facil)
from django.contrib import messages
from .models import Contrato, Factura
from .admin import ContratoForm

#Index del sistema
def index(request):
    control = request.session.get("logueado", False)
    if control:
        return render(request,"index.html")
    else: 
        messages.warning(request, "Por favor inicie sesion ...")
        return redirect ("login")
    
#Nuevo contrato

def nuevo_contrato(request):
    if request.method == 'POST':
        form = ContratoForm(request.POST)
        if form.is_valid():
            contrato = form.save(commit=False)
            contrato.confidencialidad = 'confidencialidad' in request.POST

            if "logueado" in request.session and "id" in request.session["logueado"]:
                usuario_id = request.session["logueado"]["id"]
                contrato.usuario_id = usuario_id
            else:
                messages.error(request, "Usuario no autenticado.")
                return redirect('index')
            try:
                if contrato.duracion <= 0:
                    raise ValueError("La duración debe ser mayor a cero.")
            except ValueError as e:
                messages.error(request, f"Error: {e}")
                return redirect('nuevo_contrato')

            try:
                if contrato.duracion and contrato.fecha:
                    fecha_plazo = contrato.fecha + relativedelta(months=contrato.duracion)
                    contrato.fecha_plazo = fecha_plazo  
                else:
                    messages.error(request, "Error: Fecha de inicio o duración inválida.")
                    return redirect('nuevo_contrato')
            except Exception as e:
                messages.error(request, f"Error al calcular la fecha de plazo: {e}")
                return redirect('nuevo_contrato')

            # Intentar guardar el contrato
            try:
                contrato.save()
            except Exception as e:
                messages.error(request, f"Error al guardar el contrato: {e}")
                return redirect('nuevo_contrato')

            fecha_inicio = contrato.fecha
            meses_duracion = contrato.duracion
            for i in range(meses_duracion):
                mes_factura = (fecha_inicio.month + i) % 12 or 12
                anio_factura = fecha_inicio.year + (fecha_inicio.month + i - 1) // 12
                
                factura = Factura(
                    contrato=contrato,
                    mes=mes_factura,
                    anio=anio_factura,
                    monto=contrato.precio,
                    pagado=False
                )
                factura.save()

            messages.success(request, "Contrato guardado exitosamente y facturas generadas.")
            return redirect('index')

    else:
        form = ContratoForm()

    return render(request, 'nuevo_contrato/nuevo_contrato.html', {'form': form})

def pagar_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    factura.pagado = True
    factura.save()
    return redirect('historico_contratos', user_id=factura.contrato.usuario.id)

#Historico Contratos
def historico_contratos(request, user_id):
    # Verificar si el usuario está logueado
    if "logueado" not in request.session or "id" not in request.session["logueado"]:
        return redirect('login')

    try:
        # Obtener el usuario logueado
        usuario = Usuario.objects.get(id=request.session["logueado"]["id"])
        
        # Obtener los contratos del usuario
        contratos = Contrato.objects.filter(usuario=usuario).order_by('fecha')

        # Procesar cada contrato para añadir su estado dinámico
        for contrato in contratos:
            contrato.facturas = Factura.objects.filter(contrato=contrato)

        return render(request, 'historico_contratos/historico.html', {'contratos': contratos, 'usuario_id': usuario.id})

    except Usuario.DoesNotExist:
        return redirect('login')

    
#Ingresar al sistema
def login(request):
    if request.method == "POST":
        #procesar datos
        correo = request.POST.get("correo")
        clave = request.POST.get("clave")
        #select * from Usuario where email = " " and clave = " "
        try:
            q = Usuario.objects.get(correo=correo, clave=clave)# la coma funciona como un {AND}
            messages.success(request, "Bienvenido!!")
            datos = {
                "id":q.id,
                "nombre":q.nombre,
                "apellido":q.apellido,
                "rol":q.rol
            }
            #Crear una variable de sesion (variable que tiene datos y seguirle la pista al usuario)
            request.session["logueado"] = datos #Esto es para que exita a lo largo del proyecto
            return redirect("index")
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario o Contraseña no validos D:")
            return redirect("login")
    else:
        control = request.session.get("logueado", False)
        if control == False:
            return render (request,"login/login_form.html")
        else:
            return redirect ("index")         
        
#Salir del sistema
def logout(request):
    try:
        del request.session["logueado"]
        return redirect ("login")
    except:
        messages.error(request, "Erroe, intente de nuevo D:")
        return redirect("index")
    
#Crear un nuevo perfil-formulario
def nuevo_perfil_form(request):
    if request.method == "POST":
        # Procesar los datos del formulario
        correo = request.POST.get("correo")
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        clave = request.POST.get("clave")
        rol = request.POST.get("rol")

        # Verificar si el correo ya está en uso
        if Usuario.objects.filter(correo=correo).exists():
            # Mostrar mensaje de error si el correo ya está registrado
            messages.error(request, "Correo Electronico ya existente.")
        else:
            try:
                # Crear y guardar el nuevo perfil
                query = Usuario(
                    correo=correo,
                    nombre=nombre,
                    apellido=apellido,
                    clave=clave,
                    rol=rol,
                )
                query.save()
                # Mostrar mensaje de éxito
                messages.success(request, "Perfil creado correctamente")
                # Redirigir a la página de inicio de sesión
                return redirect('login')

            except Exception as e:
                # Mostrar mensaje de error si ocurre una excepción
                messages.error(request, f"Ocurrió un error. No se guardó el perfil: {e}")
    
    return render(request, 'login/nuevperf_form.html')


#todo para el admin

#Ingresar al sistema
def login_admin(request):
    if request.method == "POST":
        codigo_ini = request.POST.get("codigo_ini")
        contraseña = request.POST.get("contraseña")
        try:
            q = Administrador.objects.get(codigo_ini=codigo_ini, contraseña=contraseña)
            messages.success(request, "Inicio de sesión exitoso")
            datos = {
                "codigo_ini":q.codigo_ini,
            }
            #Crear una variable de sesion (variable que tiene datos y seguirle la pista al usuario)
            request.session["admin"] = datos #Esto es para que exita a lo largo del proyecto
            return redirect("index_admin")
        except Administrador.DoesNotExist:
            messages.error(request, "Credenciales invalidas")
            return redirect("login_admin")
    else:
        control = request.session.get("admin", False)
        if  not control:
            return render (request,"adminn/login_admin.html")
        else:
            return redirect ("index_admin") 
        


def index_admin(request):
    control = request.session.get("admin", False)
    if control:
        lista = Usuario.objects.all()
        return render(request,"adminn/index_admin.html", {"listado": lista})
    else: 
        messages.warning(request, "debes iniciar sesion")
        return redirect ("login_admin")
    

def logout_admin(request):
    try:
        del request.session["admin"]
        return redirect ("login_admin")
    except:
        messages.error(request, "Error")
        return redirect("index_admin")
    

def admin_contrato(request, usuario_id):

    if "admin" not in request.session:
        return redirect('login_admin')

    if request.method == 'POST':
        usuario = Usuario.objects.get(id=request.session["admin"]["id"])
        form = ContratoForm(request.POST)
        if form.is_valid():
            contrato = form.save(commit=False)
            contrato.usuario = usuario  # Relaciona el contrato con el usuario
            contrato.save()
            messages.success(request, f"Contrato añadido para {usuario.nombre} {usuario.apellido}")
            return redirect('index_admin')
    else:
        form = ContratoForm()

    return render(request, 'adminn/formu_admin.html', {'form': form, 'usuario': Usuario})


#Historico Contratos
def historico_contratos_admin(request, user_id):
    control = request.session.get("admin", False)
    if not control:
        return redirect('login_admin')

    try:
        usuario = Usuario.objects.get(id= user_id)
        if request.method == "POST":
            contrato_id = request.POST.get("contrato_id")
            try:
                contrato = Contrato.objects.get(id=contrato_id, usuario=usuario)  
                contrato.pagado = True  
                contrato.save()
            except Contrato.DoesNotExist:
                pass  
                                                                                                                                                                                                                                                                                                                                            
        contratos = Contrato.objects.filter(usuario=usuario).order_by('pagado', 'fecha')
        for contrato in contratos:
                    contrato.facturas = Factura.objects.filter(contrato=contrato)
                    print(f"este es el contrato {contrato.id}")
                    print(contrato) 
        
        return render(request, 'adminn/vista_contra_admin.html', {'contratos': contratos, 'usuario_id': usuario.id})

    except Usuario.DoesNotExist:
        return redirect('login_admin')  # Redirige al login si el usuario no existe
    


def eliminar_usuario(request, id):
    control = request.session.get("admin", False)

    if not control:
        messages.info(request, "No tienes permisos para eliminar usuarios.")
        return redirect("index_admin")

    try:
        usuario = get_object_or_404(Usuario, pk=id)
        contrato = Contrato.objects.filter(usuario=usuario).first()  # Asumiendo que existe relación entre Usuario y Contrato

        if not contrato:  # Verificar si el contrato es nulo o inexistente
            usuario.delete()
            messages.success(request, "Usuario eliminado correctamente!!")
        else:
            messages.error(request, "No puedes eliminar un usuario con un contrato activo.")
    except Usuario.DoesNotExist:
        messages.error(request, "El usuario no existe.")
    except Exception as e:
        messages.error(request, f"Ocurrió un error: {str(e)}")

    return redirect("index_admin")







    """contrato = Contrato
    if control:
        messages.info(request, "Un mensaje")
        return redirect("index_admin")
    
    if not contrato:
            try:
                query = Usuario.objects.get(pk = id)
                query.delete()
                messages.success(request, "Usuario eliminado correctamente!!")
            except:
                messages.error(request, "Ocurrió un error, intente de nuevo...")

    return redirect("index_admin")"""
