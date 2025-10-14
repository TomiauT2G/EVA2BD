from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, template_views

# Crear el router y registrar los ViewSets para API
router = DefaultRouter()
router.register(r'especialidades', views.EspecialidadViewSet)
router.register(r'medicos', views.MedicoViewSet)
router.register(r'pacientes', views.PacienteViewSet)
router.register(r'consultas', views.ConsultaMedicaViewSet)
router.register(r'tratamientos', views.TratamientoViewSet)
router.register(r'medicamentos', views.MedicamentoViewSet)
router.register(r'recetas', views.RecetaMedicaViewSet)

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # Template URLs
    path('', template_views.dashboard, name='dashboard'),
    
    # Especialidades - Templates
    path('especialidades/', template_views.especialidades_list, name='especialidades_list'),
    path('especialidades/crear/', template_views.especialidades_create, name='especialidades_create'),
    path('especialidades/<int:pk>/', template_views.especialidades_detail, name='especialidades_detail'),
    path('especialidades/<int:pk>/editar/', template_views.especialidades_edit, name='especialidades_edit'),
    path('especialidades/<int:pk>/eliminar/', template_views.especialidades_delete, name='especialidades_delete'),
    
    # Pacientes - Templates
    path('pacientes/', template_views.pacientes_list, name='pacientes_list'),
    path('pacientes/crear/', template_views.pacientes_create, name='pacientes_create'),
    path('pacientes/<int:pk>/', template_views.pacientes_detail, name='pacientes_detail'),
    path('pacientes/<int:pk>/editar/', template_views.pacientes_edit, name='pacientes_edit'),
    path('pacientes/<int:pk>/eliminar/', template_views.pacientes_delete, name='pacientes_delete'),
    
    # Médicos - Templates
    path('medicos/', template_views.medicos_list, name='medicos_list'),
    path('medicos/crear/', template_views.medicos_create, name='medicos_create'),
    path('medicos/<int:pk>/', template_views.medicos_detail, name='medicos_detail'),
    path('medicos/<int:pk>/editar/', template_views.medicos_edit, name='medicos_edit'),
    path('medicos/<int:pk>/eliminar/', template_views.medicos_delete, name='medicos_delete'),
    
    # Consultas Médicas - Templates
    path('consultas/', template_views.consultas_list, name='consultas_list'),
    path('consultas/crear/', template_views.consultas_create, name='consultas_create'),
    path('consultas/<int:pk>/', template_views.consultas_detail, name='consultas_detail'),
    path('consultas/<int:pk>/editar/', template_views.consultas_edit, name='consultas_edit'),
    path('consultas/<int:pk>/eliminar/', template_views.consultas_delete, name='consultas_delete'),

    # Tratamientos - Templates
    path('tratamientos/', template_views.tratamientos_list, name='tratamientos_list'),
    path('tratamientos/crear/', template_views.tratamientos_create, name='tratamientos_create'),
    path('tratamientos/<int:pk>/', template_views.tratamientos_detail, name='tratamientos_detail'),
    path('tratamientos/<int:pk>/editar/', template_views.tratamientos_edit, name='tratamientos_edit'),
    path('tratamientos/<int:pk>/eliminar/', template_views.tratamientos_delete, name='tratamientos_delete'),

    # Medicamentos - Templates
    path('medicamentos/', template_views.medicamentos_list, name='medicamentos_list'),
    path('medicamentos/crear/', template_views.medicamentos_create, name='medicamentos_create'),
    path('medicamentos/<int:pk>/', template_views.medicamentos_detail, name='medicamentos_detail'),
    path('medicamentos/<int:pk>/editar/', template_views.medicamentos_edit, name='medicamentos_edit'),
    path('medicamentos/<int:pk>/eliminar/', template_views.medicamentos_delete, name='medicamentos_delete'),

    # Recetas Médicas - Templates
    path('recetas/', template_views.recetas_list, name='recetas_list'),
    path('recetas/crear/', template_views.recetas_create, name='recetas_create'),
    path('recetas/<int:pk>/', template_views.recetas_detail, name='recetas_detail'),
    path('recetas/<int:pk>/editar/', template_views.recetas_edit, name='recetas_edit'),
    path('recetas/<int:pk>/eliminar/', template_views.recetas_delete, name='recetas_delete'),
]