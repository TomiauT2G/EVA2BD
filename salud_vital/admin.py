from django.contrib import admin
from .models import (
    Especialidad, Medico, Paciente, ConsultaMedica, 
    Tratamiento, Medicamento, RecetaMedica
)


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'created_at']
    search_fields = ['nombre']
    list_filter = ['created_at']


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ['rut', 'nombre', 'apellido', 'especialidad', 'telefono']
    search_fields = ['rut', 'nombre', 'apellido']
    list_filter = ['especialidad', 'created_at']
    ordering = ['apellido', 'nombre']


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['rut', 'nombre', 'apellido', 'fecha_nacimiento', 'email', 'telefono']
    search_fields = ['rut', 'nombre', 'apellido', 'email']
    list_filter = ['fecha_nacimiento', 'created_at']
    ordering = ['apellido', 'nombre']


@admin.register(ConsultaMedica)
class ConsultaMedicaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'medico', 'fecha_consulta', 'motivo']
    search_fields = ['paciente__nombre', 'paciente__apellido', 'medico__nombre', 'medico__apellido']
    list_filter = ['fecha_consulta', 'medico__especialidad', 'created_at']
    ordering = ['-fecha_consulta']


@admin.register(Tratamiento)
class TratamientoAdmin(admin.ModelAdmin):
    list_display = ['consulta', 'descripcion', 'fecha_inicio', 'fecha_fin', 'esta_activo']
    search_fields = ['consulta__paciente__nombre', 'consulta__paciente__apellido', 'descripcion']
    list_filter = ['fecha_inicio', 'fecha_fin', 'created_at']
    ordering = ['-fecha_inicio']


@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'stock', 'precio_unitario', 'fecha_vencimiento', 'stock_bajo', 'proximo_vencimiento']
    search_fields = ['nombre']
    list_filter = ['fecha_vencimiento', 'created_at']
    ordering = ['nombre']


@admin.register(RecetaMedica)
class RecetaMedicaAdmin(admin.ModelAdmin):
    list_display = ['tratamiento', 'medicamento', 'cantidad', 'frecuencia', 'duracion', 'costo_total']
    search_fields = ['tratamiento__consulta__paciente__nombre', 'medicamento__nombre']
    list_filter = ['frecuencia', 'created_at']
    ordering = ['-created_at']
