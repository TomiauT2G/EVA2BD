# ============================================================================
# CONFIGURACIÓN DEL PANEL DE ADMINISTRACIÓN - SALUD VITAL
# ============================================================================
# Este archivo configura la interfaz de administración de Django para todos
# los modelos del sistema, definiendo cómo se muestran, buscan y filtran

# ============================================================================
# IMPORTACIONES NECESARIAS
# ============================================================================
from django.contrib import admin
from .models import (
    Especialidad, Medico, Paciente, ConsultaMedica, 
    Tratamiento, Medicamento, RecetaMedica
)

# ============================================================================
# CONFIGURACIÓN DE ADMINISTRACIÓN PARA ESPECIALIDADES MÉDICAS
# ============================================================================
# Gestión de especialidades con búsqueda por nombre y filtros por fecha

@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    """Configuración del admin para especialidades médicas"""
    list_display = ['nombre', 'descripcion', 'created_at']
    search_fields = ['nombre']
    list_filter = ['created_at']

# ============================================================================
# CONFIGURACIÓN DE ADMINISTRACIÓN PARA MÉDICOS
# ============================================================================
# Gestión de médicos con búsqueda por datos personales y filtros por especialidad

@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    """Configuración del admin para médicos con filtros por especialidad"""
    list_display = ['rut', 'nombre', 'apellido', 'especialidad', 'telefono']
    search_fields = ['rut', 'nombre', 'apellido']
    list_filter = ['especialidad', 'created_at']
    ordering = ['apellido', 'nombre']

# ============================================================================
# CONFIGURACIÓN DE ADMINISTRACIÓN PARA PACIENTES
# ============================================================================
# Gestión de pacientes con búsqueda por datos personales y filtros por fecha

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    """Configuración del admin para pacientes con búsqueda completa"""
    list_display = ['rut', 'nombre', 'apellido', 'fecha_nacimiento', 'email', 'telefono']
    search_fields = ['rut', 'nombre', 'apellido', 'email']
    list_filter = ['fecha_nacimiento', 'created_at']
    ordering = ['apellido', 'nombre']

# ============================================================================
# CONFIGURACIÓN DE ADMINISTRACIÓN PARA CONSULTAS MÉDICAS
# ============================================================================
# Gestión de consultas con búsqueda por paciente/médico y filtros por fecha

@admin.register(ConsultaMedica)
class ConsultaMedicaAdmin(admin.ModelAdmin):
    """Configuración del admin para consultas médicas con filtros avanzados"""
    list_display = ['paciente', 'medico', 'fecha_consulta', 'motivo']
    search_fields = ['paciente__nombre', 'paciente__apellido', 'medico__nombre', 'medico__apellido']
    list_filter = ['fecha_consulta', 'medico__especialidad', 'created_at']
    ordering = ['-fecha_consulta']

# ============================================================================
# CONFIGURACIÓN DE ADMINISTRACIÓN PARA TRATAMIENTOS
# ============================================================================
# Gestión de tratamientos con seguimiento de fechas y estado activo

@admin.register(Tratamiento)
class TratamientoAdmin(admin.ModelAdmin):
    """Configuración del admin para tratamientos con seguimiento temporal"""
    list_display = ['consulta', 'descripcion', 'fecha_inicio', 'fecha_fin', 'esta_activo']
    search_fields = ['consulta__paciente__nombre', 'consulta__paciente__apellido', 'descripcion']
    list_filter = ['fecha_inicio', 'fecha_fin', 'created_at']
    ordering = ['-fecha_inicio']

# ============================================================================
# CONFIGURACIÓN DE ADMINISTRACIÓN PARA MEDICAMENTOS
# ============================================================================
# Gestión de inventario con alertas de stock bajo y vencimiento próximo

@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    """Configuración del admin para medicamentos con alertas de inventario"""
    list_display = ['nombre', 'stock', 'precio_unitario', 'fecha_vencimiento', 'stock_bajo', 'proximo_vencimiento']
    search_fields = ['nombre']
    list_filter = ['fecha_vencimiento', 'created_at']
    ordering = ['nombre']

# ============================================================================
# CONFIGURACIÓN DE ADMINISTRACIÓN PARA RECETAS MÉDICAS
# ============================================================================
# Gestión de recetas con búsqueda por paciente/medicamento y cálculo de costos

@admin.register(RecetaMedica)
class RecetaMedicaAdmin(admin.ModelAdmin):
    """Configuración del admin para recetas médicas con cálculo de costos"""
    list_display = ['tratamiento', 'medicamento', 'cantidad', 'frecuencia', 'duracion', 'costo_total']
    search_fields = ['tratamiento__consulta__paciente__nombre', 'medicamento__nombre']
    list_filter = ['frecuencia', 'created_at']
    ordering = ['-created_at']
