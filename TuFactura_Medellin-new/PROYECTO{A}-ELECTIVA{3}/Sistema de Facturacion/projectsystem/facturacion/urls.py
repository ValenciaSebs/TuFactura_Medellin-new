from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("agregar_perfil/", views.nuevo_perfil_form, name="agregar_perfil"),  # Aquí está el nombre correcto
    path("nuevo_contrato/", views.nuevo_contrato, name="nuevo_contrato"),
    path("historico_contratos/<int:user_id>", views.historico_contratos, name="historico_contratos"),
    path("pagar_factura/<int:factura_id>/", views.pagar_factura, name="pagar_factura"),
    path("login_admin/", views.login_admin, name="login_admin"),
    path("logout_admin/", views.logout_admin, name="logout_admin"),
    path("index_admin/", views.index_admin, name="index_admin"),
    path("vista_contra/<int:user_id>/", views.historico_contratos_admin, name="vista_contra"),
    path('adminn/formu_admin<int:user_id>/', views.admin_contrato, name='formu_admin'),
    path('eliminar_usuario/<int:id>/', views.eliminar_usuario, name="eliminar_usuario"),
]