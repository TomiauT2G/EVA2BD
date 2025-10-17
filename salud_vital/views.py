# ============================================================================
# IMPORTACIONES NECESARIAS
# ============================================================================
# Importaciones de Django REST Framework para crear APIs RESTful
# Incluye viewsets, filtros, decoradores y respuestas
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

# Importaciones para filtrado avanzado con django-filter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters

# Importaciones de Django core para modelos, fechas y utilidades
from django.db import models
from datetime import datetime, timedelta

# Importaciones para vistas basadas en plantillas HTML
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

# Importaciones para formularios Django
from django.forms import ModelForm
from django import forms
from django.utils import timezone
from datetime import date, datetime, timedelta

# Importaciones de modelos locales del sistema de salud
from .models import (
    Especialidad, Medico, Paciente, ConsultaMedica, 
    Tratamiento, Medicamento, RecetaMedica, CitaMedica, HistorialClinico
)

# Importaciones de serializadores para la API REST
from .serializers import (
    EspecialidadSerializer, MedicoSerializer, PacienteSerializer,
    ConsultaMedicaSerializer, TratamientoSerializer, MedicamentoSerializer,
    RecetaMedicaSerializer, MedicoDetalleSerializer, PacienteDetalleSerializer,
    ConsultaMedicaDetalleSerializer, TratamientoDetalleSerializer
)


# ============================================================================
# FILTROS PERSONALIZADOS PARA LA API REST
# ============================================================================
# Estos filtros permiten búsquedas y filtrados avanzados en los endpoints de la API
# Cada filtro está asociado a un modelo específico y define campos de búsqueda

class MedicoFilter(django_filters.FilterSet):
    """Filtro para búsqueda de médicos por especialidad, nombre y apellido"""
    especialidad = django_filters.CharFilter(field_name='especialidad__nombre', lookup_expr='icontains')
    nombre = django_filters.CharFilter(field_name='nombre', lookup_expr='icontains')
    apellido = django_filters.CharFilter(field_name='apellido', lookup_expr='icontains')
    
    class Meta:
        model = Medico
        fields = ['especialidad', 'nombre', 'apellido']


class PacienteFilter(django_filters.FilterSet):
    """Filtro para búsqueda de pacientes por nombre, apellido y rango de edad"""
    nombre = django_filters.CharFilter(field_name='nombre', lookup_expr='icontains')
    apellido = django_filters.CharFilter(field_name='apellido', lookup_expr='icontains')
    edad_min = django_filters.NumberFilter(method='filter_edad_min')
    edad_max = django_filters.NumberFilter(method='filter_edad_max')
    
    class Meta:
        model = Paciente
        fields = ['nombre', 'apellido', 'edad_min', 'edad_max']
    
    def filter_edad_min(self, queryset, name, value):
        from datetime import date
        fecha_max = date.today().replace(year=date.today().year - value)
        return queryset.filter(fecha_nacimiento__lte=fecha_max)
    
    def filter_edad_max(self, queryset, name, value):
        from datetime import date
        fecha_min = date.today().replace(year=date.today().year - value)
        return queryset.filter(fecha_nacimiento__gte=fecha_min)


class ConsultaMedicaFilter(django_filters.FilterSet):
    """Filtro para búsqueda de consultas médicas por paciente, médico, especialidad y fechas"""
    paciente = django_filters.CharFilter(field_name='paciente__nombre', lookup_expr='icontains')
    medico = django_filters.CharFilter(field_name='medico__nombre', lookup_expr='icontains')
    especialidad = django_filters.CharFilter(field_name='medico__especialidad__nombre', lookup_expr='icontains')
    fecha_desde = django_filters.DateFilter(field_name='fecha_consulta', lookup_expr='gte')
    fecha_hasta = django_filters.DateFilter(field_name='fecha_consulta', lookup_expr='lte')
    
    class Meta:
        model = ConsultaMedica
        fields = ['paciente', 'medico', 'especialidad', 'fecha_desde', 'fecha_hasta']


class MedicamentoFilter(django_filters.FilterSet):
    """Filtro para búsqueda de medicamentos con alertas de stock bajo y próximo vencimiento"""
    nombre = django_filters.CharFilter(field_name='nombre', lookup_expr='icontains')
    stock_bajo = django_filters.BooleanFilter(method='filter_stock_bajo')
    proximo_vencimiento = django_filters.BooleanFilter(method='filter_proximo_vencimiento')
    
    class Meta:
        model = Medicamento
        fields = ['nombre', 'stock_bajo', 'proximo_vencimiento']
    
    def filter_stock_bajo(self, queryset, name, value):
        if value:
            return queryset.filter(stock__lte=10)
        return queryset.filter(stock__gt=10)
    
    def filter_proximo_vencimiento(self, queryset, name, value):
        from datetime import date, timedelta
        fecha_limite = date.today() + timedelta(days=30)
        if value:
            return queryset.filter(fecha_vencimiento__lte=fecha_limite)
        return queryset.filter(fecha_vencimiento__gt=fecha_limite)


# ============================================================================
# VIEWSETS PARA LA API REST
# ============================================================================
# Estos viewsets proporcionan endpoints CRUD completos para cada modelo
# Incluyen funcionalidades de filtrado, búsqueda, ordenamiento y acciones personalizadas

class EspecialidadViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar especialidades médicas a través de la API REST"""
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'created_at']
    ordering = ['nombre']


class MedicoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar médicos con filtrado por especialidad y acciones personalizadas"""
    queryset = Medico.objects.select_related('especialidad')
    serializer_class = MedicoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MedicoFilter
    search_fields = ['rut', 'nombre', 'apellido', 'especialidad__nombre']
    ordering_fields = ['nombre', 'apellido', 'especialidad__nombre', 'created_at']
    ordering = ['apellido', 'nombre']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MedicoDetalleSerializer
        return MedicoSerializer
    
    @action(detail=True, methods=['get'])
    def consultas(self, request, pk=None):
        """Obtener consultas de un médico específico"""
        medico = self.get_object()
        consultas = medico.consultas_realizadas.all()
        serializer = ConsultaMedicaSerializer(consultas, many=True)
        return Response(serializer.data)


class PacienteViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar pacientes con filtrado por edad y datos personales"""
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PacienteFilter
    search_fields = ['rut', 'nombre', 'apellido']
    ordering_fields = ['nombre', 'apellido', 'fecha_nacimiento', 'created_at']
    ordering = ['apellido', 'nombre']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PacienteDetalleSerializer
        return PacienteSerializer
    
    @action(detail=True, methods=['get'])
    def consultas(self, request, pk=None):
        """Obtener consultas de un paciente específico"""
        paciente = self.get_object()
        consultas = paciente.consultas.all()
        serializer = ConsultaMedicaSerializer(consultas, many=True)
        return Response(serializer.data)


class ConsultaMedicaViewSet(viewsets.ModelViewSet):
    queryset = ConsultaMedica.objects.select_related('paciente', 'medico', 'medico__especialidad')
    serializer_class = ConsultaMedicaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ConsultaMedicaFilter
    search_fields = ['paciente__nombre', 'paciente__apellido', 'medico__nombre', 'medico__apellido', 'motivo']
    ordering_fields = ['fecha_consulta', 'created_at']
    ordering = ['-fecha_consulta']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ConsultaMedicaDetalleSerializer
        return ConsultaMedicaSerializer
    
    @action(detail=False, methods=['get'])
    def hoy(self, request):
        """Obtener consultas de hoy"""
        hoy = datetime.now().date()
        consultas = self.queryset.filter(fecha_consulta__date=hoy)
        serializer = self.get_serializer(consultas, many=True)
        return Response(serializer.data)


class TratamientoViewSet(viewsets.ModelViewSet):
    queryset = Tratamiento.objects.select_related('consulta', 'consulta__paciente', 'consulta__medico')
    serializer_class = TratamientoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['consulta__paciente__nombre', 'consulta__paciente__apellido', 'descripcion']
    ordering_fields = ['fecha_inicio', 'fecha_fin', 'created_at']
    ordering = ['-fecha_inicio']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TratamientoDetalleSerializer
        return TratamientoSerializer
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Obtener tratamientos activos"""
        from datetime import date
        tratamientos = self.queryset.filter(
            models.Q(fecha_fin__isnull=True) | models.Q(fecha_fin__gte=date.today())
        )
        serializer = self.get_serializer(tratamientos, many=True)
        return Response(serializer.data)


class MedicamentoViewSet(viewsets.ModelViewSet):
    queryset = Medicamento.objects.all()
    serializer_class = MedicamentoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MedicamentoFilter
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'stock', 'precio_unitario', 'fecha_vencimiento', 'created_at']
    ordering = ['nombre']
    
    @action(detail=False, methods=['get'])
    def stock_bajo(self, request):
        """Obtener medicamentos con stock bajo"""
        medicamentos = self.queryset.filter(stock__lte=10)
        serializer = self.get_serializer(medicamentos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def proximos_vencimiento(self, request):
        """Obtener medicamentos próximos a vencer"""
        from datetime import date, timedelta
        fecha_limite = date.today() + timedelta(days=30)
        medicamentos = self.queryset.filter(fecha_vencimiento__lte=fecha_limite)
        serializer = self.get_serializer(medicamentos, many=True)
        return Response(serializer.data)


class RecetaMedicaViewSet(viewsets.ModelViewSet):
    queryset = RecetaMedica.objects.select_related(
        'tratamiento', 'tratamiento__consulta', 'tratamiento__consulta__paciente', 'medicamento'
    )
    serializer_class = RecetaMedicaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['tratamiento__consulta__paciente__nombre', 'medicamento__nombre']
    ordering_fields = ['created_at', 'cantidad', 'frecuencia']
    ordering = ['-created_at']


# ============================================================================
# FORMULARIOS PARA VISTAS BASADAS EN PLANTILLAS HTML
# ============================================================================
# Estos formularios definen la estructura y validación para las vistas web
# Incluyen estilos CSS personalizados con Tailwind CSS para una interfaz moderna

class EspecialidadForm(ModelForm):
    """Formulario para crear y editar especialidades médicas"""
    class Meta:
        model = Especialidad
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'placeholder': 'Ej: Cardiología'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'rows': 3,
                'placeholder': 'Descripción de la especialidad...'
            }),
        }

class PacienteForm(ModelForm):
    class Meta:
        model = Paciente
        fields = ['rut', 'nombre', 'apellido', 'fecha_nacimiento', 'telefono', 'email', 'direccion']
        widgets = {
            'rut': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'placeholder': '12.345.678-9'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'placeholder': 'Nombre del paciente'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'placeholder': 'Apellido del paciente'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'type': 'date'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'placeholder': '+56 9 1234 5678'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'placeholder': 'correo@ejemplo.com'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'rows': 2,
                'placeholder': 'Dirección completa'
            }),
        }

class MedicoForm(ModelForm):
    class Meta:
        model = Medico
        fields = ['rut', 'nombre', 'apellido', 'telefono', 'email', 'especialidad', 'activo']
        widgets = {
            'rut': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'placeholder': '12.345.678-9'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'placeholder': 'Nombre del médico'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'placeholder': 'Apellido del médico'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'placeholder': '+56 9 1234 5678'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'placeholder': 'correo@ejemplo.com'
            }),
            'especialidad': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 focus:ring-2'
            }),
        }

class ConsultaForm(forms.ModelForm):
    class Meta:
        model = ConsultaMedica
        fields = ['paciente', 'medico', 'cita', 'fecha_consulta', 'motivo', 'diagnostico']
        widgets = {
            'paciente': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'required': True
            }),
            'medico': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'required': True
            }),
            'cita': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200'
            }),
            'fecha_consulta': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'type': 'datetime-local',
                'required': True
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'rows': 4,
                'required': True
            }),
            'diagnostico': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'rows': 4
            }),
        }

class TratamientoForm(forms.ModelForm):
    class Meta:
        model = Tratamiento
        fields = ['consulta', 'descripcion', 'fecha_inicio', 'fecha_fin']
        widgets = {
            'consulta': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'required': True
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'rows': 4,
                'required': True
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'type': 'date',
                'required': True
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'type': 'date'
            }),
        }

class MedicamentoForm(forms.ModelForm):
    class Meta:
        model = Medicamento
        fields = ['nombre', 'descripcion', 'stock', 'precio_unitario', 'fecha_vencimiento']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'required': True
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'rows': 3
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'min': 0,
                'required': True
            }),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'step': '0.01',
                'min': '0',
                'required': True
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'type': 'date',
                'required': True
            }),
        }

class RecetaMedicaForm(forms.ModelForm):
    class Meta:
        model = RecetaMedica
        fields = ['tratamiento', 'medicamento', 'cantidad', 'frecuencia', 'duracion']
        widgets = {
            'tratamiento': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'required': True
            }),
            'medicamento': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'required': True
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'min': 1,
                'required': True
            }),
            'frecuencia': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'required': True
            }),
            'duracion': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'required': True
            }),
        }


# ============================================================================
# VISTAS BASADAS EN PLANTILLAS HTML
# ============================================================================
# Estas vistas manejan la interfaz web del sistema, proporcionando páginas HTML
# completas con funcionalidades CRUD, paginación, búsqueda y filtrado

# ============================================================================
# DASHBOARD PRINCIPAL
# ============================================================================
def dashboard(request):
    """Vista principal del dashboard con estadísticas generales del sistema"""
    """Vista principal del dashboard"""
    # Estadísticas generales
    total_pacientes = Paciente.objects.count()
    total_medicos = Medico.objects.count()
    total_especialidades = Especialidad.objects.count()
    total_consultas = ConsultaMedica.objects.count()
    
    # Consultas de hoy
    hoy = date.today()
    consultas_hoy = ConsultaMedica.objects.filter(fecha_consulta__date=hoy).count()
    
    # Consultas recientes
    consultas_recientes = ConsultaMedica.objects.select_related(
        'paciente', 'medico', 'medico__especialidad'
    ).order_by('-fecha_consulta')[:5]
    
    # Estadísticas por especialidad
    especialidades_stats = Especialidad.objects.annotate(
        total_medicos=Count('medicos'),
        total_consultas=Count('medicos__consultas_realizadas')
    ).order_by('-total_consultas')[:5]
    
    context = {
        'total_pacientes': total_pacientes,
        'total_medicos': total_medicos,
        'total_especialidades': total_especialidades,
        'total_consultas': total_consultas,
        'consultas_hoy': consultas_hoy,
        'consultas_recientes': consultas_recientes,
        'especialidades_stats': especialidades_stats,
    }
    
    return render(request, 'dashboard.html', context)


# ============================================================================
# GESTIÓN DE ESPECIALIDADES MÉDICAS
# ============================================================================
# Vistas para el manejo completo de especialidades: listado, creación, 
# visualización, edición y eliminación

def especialidades_list(request):
    """Vista para listar todas las especialidades con búsqueda y paginación"""
    """Lista de especialidades"""
    search = request.GET.get('search', '')
    especialidades = Especialidad.objects.all()
    
    if search:
        especialidades = especialidades.filter(
            Q(nombre__icontains=search) | Q(descripcion__icontains=search)
        )
    
    especialidades = especialidades.annotate(
        total_medicos=Count('medicos')
    ).order_by('nombre')
    
    paginator = Paginator(especialidades, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'especialidades': page_obj,
        'is_paginated': page_obj.paginator.num_pages > 1,
        'search': search,
    }
    
    return render(request, 'especialidades/list.html', context)


def especialidades_create(request):
    """Crear nueva especialidad"""
    if request.method == 'POST':
        form = EspecialidadForm(request.POST)
        if form.is_valid():
            especialidad = form.save()
            messages.success(request, f'Especialidad "{especialidad.nombre}" creada exitosamente.')
            return redirect('especialidades_detail', pk=especialidad.pk)
    else:
        form = EspecialidadForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'especialidades/create.html', context)


def especialidades_detail(request, pk):
    """Detalle de especialidad"""
    especialidad = get_object_or_404(Especialidad, pk=pk)
    medicos = especialidad.medicos.all()
    
    context = {
        'especialidad': especialidad,
        'medicos': medicos,
    }
    
    return render(request, 'especialidades/detail.html', context)


def especialidades_edit(request, pk):
    """Editar especialidad"""
    especialidad = get_object_or_404(Especialidad, pk=pk)
    
    if request.method == 'POST':
        form = EspecialidadForm(request.POST, instance=especialidad)
        if form.is_valid():
            form.save()
            messages.success(request, f'Especialidad "{especialidad.nombre}" actualizada exitosamente.')
            return redirect('especialidades_detail', pk=especialidad.pk)
    else:
        form = EspecialidadForm(instance=especialidad)
    
    context = {
        'form': form,
        'especialidad': especialidad,
    }
    
    return render(request, 'especialidades/edit.html', context)


@require_http_methods(["POST"])
def especialidades_delete(request, pk):
    """Eliminar especialidad"""
    especialidad = get_object_or_404(Especialidad, pk=pk)
    nombre = especialidad.nombre
    
    try:
        especialidad.delete()
        messages.success(request, f'Especialidad "{nombre}" eliminada exitosamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar la especialidad: {str(e)}')
    
    return redirect('especialidades_list')


# ============================================================================
# GESTIÓN DE PACIENTES
# ============================================================================
# Vistas para el manejo completo de pacientes: listado con filtros avanzados,
# creación, visualización de perfil, edición y eliminación

def pacientes_list(request):
    """Vista para listar pacientes con filtros por nombre, apellido y grupo sanguíneo"""
    """Lista de pacientes"""
    search = request.GET.get('search', '')
    
    pacientes = Paciente.objects.all()
    
    if search:
        pacientes = pacientes.filter(
            Q(nombre__icontains=search) | 
            Q(apellido__icontains=search) |
            Q(rut__icontains=search)
        )
    
    pacientes = pacientes.order_by('apellido', 'nombre')
    
    paginator = Paginator(pacientes, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    total_pacientes = Paciente.objects.count()
    consultas_mes = ConsultaMedica.objects.filter(
        fecha_consulta__month=timezone.now().month,
        fecha_consulta__year=timezone.now().year
    ).count()
    
    context = {
        'page_obj': page_obj,
        'pacientes': page_obj,
        'is_paginated': page_obj.paginator.num_pages > 1,
        'search': search,
        'total_pacientes': total_pacientes,
        'consultas_mes': consultas_mes,
    }
    
    return render(request, 'pacientes/list.html', context)


def pacientes_create(request):
    """Crear nuevo paciente"""
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save()
            messages.success(request, f'Paciente "{paciente.nombre} {paciente.apellido}" creado exitosamente.')
            return redirect('pacientes_detail', pk=paciente.pk)
    else:
        form = PacienteForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'pacientes/create.html', context)


def pacientes_detail(request, pk):
    """Detalle de paciente"""
    paciente = get_object_or_404(Paciente, pk=pk)
    consultas = paciente.consultas.select_related(
        'medico', 'medico__especialidad'
    ).order_by('-fecha_consulta')
    
    context = {
        'paciente': paciente,
        'consultas': consultas,
    }
    
    return render(request, 'pacientes/detail.html', context)


def pacientes_edit(request, pk):
    """Editar paciente"""
    paciente = get_object_or_404(Paciente, pk=pk)
    
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, f'Paciente "{paciente.nombre} {paciente.apellido}" actualizado exitosamente.')
            return redirect('pacientes_detail', pk=paciente.pk)
    else:
        form = PacienteForm(instance=paciente)
    
    context = {
        'form': form,
        'paciente': paciente,
    }
    
    return render(request, 'pacientes/edit.html', context)


@require_http_methods(["POST"])
def pacientes_delete(request, pk):
    """Eliminar paciente"""
    paciente = get_object_or_404(Paciente, pk=pk)
    nombre = f"{paciente.nombre} {paciente.apellido}"
    
    try:
        # Verificar si el paciente tiene registros relacionados
        citas_count = paciente.citas.count()
        consultas_count = paciente.consultas.count()
        
        if citas_count > 0 or consultas_count > 0:
            # Eliminar registros relacionados en orden correcto
            # Primero eliminar recetas médicas (relacionadas con tratamientos)
            for consulta in paciente.consultas.all():
                for tratamiento in consulta.tratamientos.all():
                    tratamiento.recetas.all().delete()
                    tratamiento.delete()
                consulta.delete()
            
            # Eliminar citas médicas
            paciente.citas.all().delete()
            
            # Eliminar historial clínico si existe
            if hasattr(paciente, 'historial_clinico'):
                paciente.historial_clinico.delete()
        
        # Finalmente eliminar el paciente
        paciente.delete()
        
        if citas_count > 0 or consultas_count > 0:
            messages.success(request, f'Paciente "{nombre}" y todos sus registros relacionados ({citas_count} citas, {consultas_count} consultas) eliminados exitosamente.')
        else:
            messages.success(request, f'Paciente "{nombre}" eliminado exitosamente.')
            
    except Exception as e:
        messages.error(request, f'Error al eliminar el paciente: {str(e)}')
    
    return redirect('pacientes_list')


# ============================================================================
# GESTIÓN DE MÉDICOS
# ============================================================================
# Vistas para el manejo completo de médicos: listado con filtros por especialidad,
# creación, visualización de perfil, edición y eliminación

def medicos_list(request):
    """Vista para listar médicos con filtros por especialidad y estado activo"""
    """Lista de médicos"""
    search = request.GET.get('search', '')
    especialidad = request.GET.get('especialidad', '')
    
    medicos = Medico.objects.select_related('especialidad')
    
    if search:
        medicos = medicos.filter(
            Q(nombre__icontains=search) | 
            Q(apellido__icontains=search) |
            Q(rut__icontains=search)
        )
    
    if especialidad:
        medicos = medicos.filter(especialidad_id=especialidad)
    
    medicos = medicos.order_by('apellido', 'nombre')
    
    paginator = Paginator(medicos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    especialidades = Especialidad.objects.all().order_by('nombre')
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'especialidad': especialidad,
        'especialidades': especialidades,
    }
    
    return render(request, 'medicos/list.html', context)


def medicos_create(request):
    """Crear nuevo médico"""
    if request.method == 'POST':
        form = MedicoForm(request.POST)
        if form.is_valid():
            medico = form.save()
            messages.success(request, f'Médico "Dr. {medico.nombre} {medico.apellido}" creado exitosamente.')
            return redirect('medicos_detail', pk=medico.pk)
    else:
        form = MedicoForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'medicos/create.html', context)


def medicos_detail(request, pk):
    """Detalle de médico"""
    medico = get_object_or_404(Medico, pk=pk)
    consultas = medico.consultas_realizadas.select_related(
        'paciente'
    ).order_by('-fecha_consulta')
    
    context = {
        'medico': medico,
        'consultas': consultas,
    }
    
    return render(request, 'medicos/detail.html', context)


def medicos_edit(request, pk):
    """Editar médico"""
    medico = get_object_or_404(Medico, pk=pk)
    
    if request.method == 'POST':
        form = MedicoForm(request.POST, instance=medico)
        if form.is_valid():
            form.save()
            messages.success(request, f'Médico "Dr. {medico.nombre} {medico.apellido}" actualizado exitosamente.')
            return redirect('medicos_detail', pk=medico.pk)
    else:
        form = MedicoForm(instance=medico)
    
    context = {
        'form': form,
        'medico': medico,
    }
    
    return render(request, 'medicos/edit.html', context)


@require_http_methods(["POST"])
def medicos_delete(request, pk):
    """Eliminar médico"""
    medico = get_object_or_404(Medico, pk=pk)
    nombre = f"Dr. {medico.nombre} {medico.apellido}"
    
    try:
        medico.delete()
        messages.success(request, f'Médico "{nombre}" eliminado exitosamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el médico: {str(e)}')
    
    return redirect('medicos_list')


# ============================================================================
# GESTIÓN DE CONSULTAS MÉDICAS
# ============================================================================
# Vistas para el manejo de consultas médicas: listado con filtros por fecha,
# médico y paciente, creación, visualización y edición

def consultas_list(request):
    """Vista para listar consultas médicas con filtros avanzados por fecha y participantes"""
    """Lista de consultas médicas"""
    search = request.GET.get('search', '')
    medico = request.GET.get('medico', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    consultas = ConsultaMedica.objects.select_related('paciente', 'medico', 'medico__especialidad')
    
    if search:
        consultas = consultas.filter(
            Q(paciente__nombre__icontains=search) | 
            Q(paciente__apellido__icontains=search) |
            Q(medico__nombre__icontains=search) |
            Q(medico__apellido__icontains=search) |
            Q(diagnostico__icontains=search) |
            Q(motivo__icontains=search)
        )
    
    if medico:
        consultas = consultas.filter(medico_id=medico)
    
    if fecha_desde:
        consultas = consultas.filter(fecha_consulta__date__gte=fecha_desde)
    
    if fecha_hasta:
        consultas = consultas.filter(fecha_consulta__date__lte=fecha_hasta)
    
    consultas = consultas.order_by('-fecha_consulta')
    
    paginator = Paginator(consultas, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    medicos = Medico.objects.select_related('especialidad').order_by('apellido', 'nombre')
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'medico': medico,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'medicos': medicos,
    }
    
    return render(request, 'consultas/list.html', context)


def consultas_create(request):
    """Crear nueva consulta médica"""
    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            consulta = form.save()
            messages.success(request, f'Consulta médica registrada exitosamente.')
            return redirect('consultas_detail', pk=consulta.pk)
    else:
        form = ConsultaForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'consultas/create.html', context)


def consultas_detail(request, pk):
    """Detalle de consulta médica"""
    consulta = get_object_or_404(ConsultaMedica, pk=pk)
    
    context = {
        'consulta': consulta,
    }
    
    return render(request, 'consultas/detail.html', context)


def consultas_edit(request, pk):
    """Editar consulta médica"""
    consulta = get_object_or_404(ConsultaMedica, pk=pk)
    
    if request.method == 'POST':
        form = ConsultaForm(request.POST, instance=consulta)
        if form.is_valid():
            form.save()
            messages.success(request, f'Consulta médica actualizada exitosamente.')
            return redirect('consultas_detail', pk=consulta.pk)
    else:
        form = ConsultaForm(instance=consulta)
    
    context = {
        'form': form,
        'consulta': consulta,
    }
    
    return render(request, 'consultas/edit.html', context)


@require_http_methods(["POST"])
def consultas_delete(request, pk):
    """Eliminar consulta médica"""
    consulta = get_object_or_404(ConsultaMedica, pk=pk)
    
    try:
        consulta.delete()
        messages.success(request, f'Consulta médica eliminada exitosamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar la consulta: {str(e)}')
    
    return redirect('consultas_list')


# ============================================================================
# GESTIÓN DE TRATAMIENTOS
# ============================================================================
# Vistas para el manejo de tratamientos médicos: listado con estado activo/inactivo,
# creación, visualización y edición con fechas de seguimiento

def tratamientos_list(request):
    """Vista para listar tratamientos con filtros por estado y fechas"""
    """Lista de tratamientos"""
    search_query = request.GET.get('search', '')
    consulta_filter = request.GET.get('consulta', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    tratamientos = Tratamiento.objects.all().order_by('-fecha_inicio')
    
    if search_query:
        tratamientos = tratamientos.filter(
            Q(descripcion__icontains=search_query) |
            Q(consulta__paciente__nombre__icontains=search_query) |
            Q(consulta__paciente__apellido__icontains=search_query)
        )
    
    if consulta_filter:
        tratamientos = tratamientos.filter(consulta_id=consulta_filter)
    
    if fecha_desde:
        tratamientos = tratamientos.filter(fecha_inicio__gte=fecha_desde)
    
    if fecha_hasta:
        tratamientos = tratamientos.filter(fecha_inicio__lte=fecha_hasta)
    
    paginator = Paginator(tratamientos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    consultas = ConsultaMedica.objects.all()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'consulta_filter': consulta_filter,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'consultas': consultas,
    }
    return render(request, 'tratamientos/list.html', context)


def tratamientos_create(request):
    """Crear nuevo tratamiento"""
    if request.method == 'POST':
        form = TratamientoForm(request.POST)
        if form.is_valid():
            tratamiento = form.save()
            messages.success(request, f'Tratamiento creado exitosamente.')
            return redirect('tratamientos_detail', pk=tratamiento.pk)
    else:
        form = TratamientoForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'tratamientos/create.html', context)


def tratamientos_detail(request, pk):
    """Detalle de tratamiento"""
    tratamiento = get_object_or_404(Tratamiento, pk=pk)
    
    context = {
        'tratamiento': tratamiento,
    }
    
    return render(request, 'tratamientos/detail.html', context)


def tratamientos_edit(request, pk):
    """Editar tratamiento"""
    tratamiento = get_object_or_404(Tratamiento, pk=pk)
    
    if request.method == 'POST':
        form = TratamientoForm(request.POST, instance=tratamiento)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tratamiento actualizado exitosamente.')
            return redirect('tratamientos_detail', pk=tratamiento.pk)
    else:
        form = TratamientoForm(instance=tratamiento)
    
    context = {
        'form': form,
        'tratamiento': tratamiento,
    }
    
    return render(request, 'tratamientos/edit.html', context)


@require_http_methods(["POST"])
def tratamientos_delete(request, pk):
    """Eliminar tratamiento"""
    tratamiento = get_object_or_404(Tratamiento, pk=pk)
    
    try:
        tratamiento.delete()
        messages.success(request, f'Tratamiento eliminado exitosamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el tratamiento: {str(e)}')
    
    return redirect('tratamientos_list')


# ============================================================================
# GESTIÓN DE MEDICAMENTOS
# ============================================================================
# Vistas para el manejo de inventario de medicamentos: listado con alertas de stock
# bajo y vencimiento próximo, creación, visualización y edición

def medicamentos_list(request):
    """Vista para listar medicamentos con alertas de stock y vencimiento"""
    """Lista de medicamentos"""
    search = request.GET.get('search', '')
    stock_bajo = request.GET.get('stock_bajo', '')
    proximo_vencimiento = request.GET.get('proximo_vencimiento', '')
    
    medicamentos = Medicamento.objects.all()
    
    if search:
        medicamentos = medicamentos.filter(
            Q(nombre__icontains=search) | 
            Q(descripcion__icontains=search)
        )
    
    if stock_bajo:
        medicamentos = medicamentos.filter(stock__lte=10)
    
    if proximo_vencimiento:
        from datetime import date, timedelta
        fecha_limite = date.today() + timedelta(days=30)
        medicamentos = medicamentos.filter(fecha_vencimiento__lte=fecha_limite)
    
    medicamentos = medicamentos.order_by('nombre')
    
    paginator = Paginator(medicamentos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'medicamentos': page_obj,  # Para compatibilidad con la plantilla
        'paginator': paginator,
        'search': search,
        'stock_bajo': stock_bajo,
        'proximo_vencimiento': proximo_vencimiento,
        'is_paginated': page_obj.paginator.num_pages > 1,
    }
    
    return render(request, 'medicamentos/list.html', context)


def medicamentos_create(request):
    """Crear nuevo medicamento"""
    if request.method == 'POST':
        form = MedicamentoForm(request.POST)
        if form.is_valid():
            medicamento = form.save()
            messages.success(request, f'Medicamento "{medicamento.nombre}" creado exitosamente.')
            return redirect('medicamentos_detail', pk=medicamento.pk)
    else:
        form = MedicamentoForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'medicamentos/create.html', context)


def medicamentos_detail(request, pk):
    """Detalle de medicamento"""
    medicamento = get_object_or_404(Medicamento, pk=pk)
    
    context = {
        'medicamento': medicamento,
    }
    
    return render(request, 'medicamentos/detail.html', context)


def medicamentos_edit(request, pk):
    """Editar medicamento"""
    medicamento = get_object_or_404(Medicamento, pk=pk)
    
    if request.method == 'POST':
        form = MedicamentoForm(request.POST, instance=medicamento)
        if form.is_valid():
            form.save()
            messages.success(request, f'Medicamento "{medicamento.nombre}" actualizado exitosamente.')
            return redirect('medicamentos_detail', pk=medicamento.pk)
    else:
        form = MedicamentoForm(instance=medicamento)
    
    context = {
        'form': form,
        'medicamento': medicamento,
    }
    
    return render(request, 'medicamentos/edit.html', context)


@require_http_methods(["POST"])
def medicamentos_delete(request, pk):
    """Eliminar medicamento"""
    medicamento = get_object_or_404(Medicamento, pk=pk)
    nombre = medicamento.nombre
    
    try:
        medicamento.delete()
        messages.success(request, f'Medicamento "{nombre}" eliminado exitosamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el medicamento: {str(e)}')
    
    return redirect('medicamentos_list')


# ==================== RECETAS MÉDICAS ====================

def recetas_list(request):
    """Lista de recetas médicas"""
    search = request.GET.get('search', '')
    medico = request.GET.get('medico', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    recetas = RecetaMedica.objects.select_related(
        'tratamiento', 'tratamiento__consulta', 'tratamiento__consulta__paciente', 
        'tratamiento__consulta__medico', 'tratamiento__consulta__medico__especialidad', 'medicamento'
    )
    
    if search:
        recetas = recetas.filter(
            Q(tratamiento__consulta__paciente__nombre__icontains=search) |
            Q(tratamiento__consulta__paciente__apellido__icontains=search) |
            Q(tratamiento__consulta__medico__nombre__icontains=search) |
            Q(tratamiento__consulta__medico__apellido__icontains=search) |
            Q(medicamento__nombre__icontains=search)
        )
    
    if medico:
        recetas = recetas.filter(tratamiento__consulta__medico_id=medico)
    
    if fecha_desde:
        recetas = recetas.filter(created_at__date__gte=fecha_desde)
    
    if fecha_hasta:
        recetas = recetas.filter(created_at__date__lte=fecha_hasta)
    
    recetas = recetas.order_by('-created_at')
    
    # Estadísticas para el dashboard
    from datetime import date, timedelta
    today = date.today()
    total_recetas = recetas.count()
    recetas_activas = recetas.filter(created_at__date__gte=today - timedelta(days=30)).count()
    recetas_vencidas = 0  # Placeholder - necesitaríamos un campo de fecha de vencimiento
    recetas_hoy = recetas.filter(created_at__date=today).count()
    
    paginator = Paginator(recetas, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener médicos para el filtro
    medicos = Medico.objects.select_related('especialidad').order_by('apellido', 'nombre')
    
    context = {
        'page_obj': page_obj,
        'recetas': page_obj,  # Para compatibilidad con la plantilla
        'paginator': paginator,
        'search': search,
        'medico': medico,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'medicos': medicos,
        'is_paginated': page_obj.paginator.num_pages > 1,
        # Estadísticas
        'total_recetas': total_recetas,
        'recetas_activas': recetas_activas,
        'recetas_vencidas': recetas_vencidas,
        'recetas_hoy': recetas_hoy,
    }
    
    return render(request, 'recetas/list.html', context)


def recetas_create(request):
    """Crear nueva receta médica"""
    if request.method == 'POST':
        form = RecetaMedicaForm(request.POST)
        if form.is_valid():
            receta = form.save()
            messages.success(request, f'Receta médica creada exitosamente.')
            return redirect('recetas_detail', pk=receta.pk)
    else:
        form = RecetaMedicaForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'recetas/create.html', context)


def recetas_detail(request, pk):
    """Detalle de receta médica"""
    receta = get_object_or_404(RecetaMedica, pk=pk)
    
    context = {
        'receta': receta,
    }
    
    return render(request, 'recetas/detail.html', context)


def recetas_edit(request, pk):
    """Editar receta médica"""
    receta = get_object_or_404(RecetaMedica, pk=pk)
    
    if request.method == 'POST':
        form = RecetaMedicaForm(request.POST, instance=receta)
        if form.is_valid():
            form.save()
            messages.success(request, f'Receta médica actualizada exitosamente.')
            return redirect('recetas_detail', pk=receta.pk)
    else:
        form = RecetaMedicaForm(instance=receta)
    
    context = {
        'form': form,
        'receta': receta,
    }
    
    return render(request, 'recetas/edit.html', context)


@require_http_methods(["POST"])
def recetas_delete(request, pk):
    """Eliminar receta médica"""
    receta = get_object_or_404(RecetaMedica, pk=pk)
    
    try:
        receta.delete()
        messages.success(request, f'Receta médica eliminada exitosamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar la receta: {str(e)}')
    
    return redirect('recetas_list')


# ==================== CITAS MÉDICAS ====================

class CitaForm(forms.ModelForm):
    class Meta:
        model = CitaMedica
        fields = ['paciente', 'medico', 'fecha_hora_cita', 'estado', 'motivo', 'observaciones']
        widgets = {
            'paciente': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'required': True
            }),
            'medico': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'required': True
            }),
            'fecha_hora_cita': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'type': 'datetime-local',
                'required': True
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200'
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'rows': 3,
                'placeholder': 'Describa el motivo de la cita médica...'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
        }

def citas_list(request):
    """Lista de citas médicas"""
    search = request.GET.get('search', '')
    estado = request.GET.get('estado', '')
    
    citas = CitaMedica.objects.select_related('paciente', 'medico', 'medico__especialidad').all()
    
    if search:
        citas = citas.filter(
            Q(paciente__nombre__icontains=search) | 
            Q(paciente__apellido__icontains=search) |
            Q(medico__nombre__icontains=search) |
            Q(medico__apellido__icontains=search)
        )
    
    if estado:
        citas = citas.filter(estado=estado)
    
    citas = citas.order_by('-fecha_hora_cita')
    
    paginator = Paginator(citas, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    total_citas = CitaMedica.objects.count()
    citas_hoy = CitaMedica.objects.filter(
        fecha_hora_cita__date=timezone.now().date()
    ).count()
    
    context = {
        'page_obj': page_obj,
        'citas': page_obj,
        'is_paginated': page_obj.paginator.num_pages > 1,
        'search': search,
        'estado': estado,
        'total_citas': total_citas,
        'citas_hoy': citas_hoy,
        'estados': CitaMedica.ESTADO_CHOICES,
    }
    
    return render(request, 'citas/list.html', context)

def citas_detail(request, pk):
    """Detalle de cita médica"""
    cita = get_object_or_404(CitaMedica.objects.select_related('paciente', 'medico', 'medico__especialidad'), pk=pk)
    
    context = {
        'cita': cita,
    }
    
    return render(request, 'citas/detail.html', context)

def citas_create(request):
    """Crear nueva cita médica"""
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            try:
                cita = form.save()
                messages.success(request, f'Cita médica creada exitosamente para {cita.paciente.nombre_completo}.')
                return redirect('citas_detail', pk=cita.pk)
            except Exception as e:
                messages.error(request, f'Error al crear la cita: {str(e)}')
    else:
        form = CitaForm()
    
    context = {
        'form': form,
        'title': 'Nueva Cita Médica',
    }
    
    return render(request, 'citas/create.html', context)

def citas_edit(request, pk):
    """Editar cita médica"""
    cita = get_object_or_404(CitaMedica, pk=pk)
    
    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            try:
                cita = form.save()
                messages.success(request, f'Cita médica actualizada exitosamente.')
                return redirect('citas_detail', pk=cita.pk)
            except Exception as e:
                messages.error(request, f'Error al actualizar la cita: {str(e)}')
    else:
        form = CitaForm(instance=cita)
    
    context = {
        'form': form,
        'cita': cita,
        'title': 'Editar Cita Médica',
    }
    
    return render(request, 'citas/edit.html', context)

@require_http_methods(["POST"])
def citas_delete(request, pk):
    """Eliminar cita médica"""
    cita = get_object_or_404(CitaMedica, pk=pk)
    
    try:
        cita.delete()
        messages.success(request, f'Cita médica eliminada exitosamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar la cita: {str(e)}')
    
    return redirect('citas_list')


# ==================== HISTORIAL CLÍNICO ====================

class HistorialForm(forms.ModelForm):
    # Campos adicionales que no están en el modelo pero se necesitan en el template
    peso = forms.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
            'placeholder': 'Peso en kg',
            'step': '0.1',
            'min': '0'
        })
    )
    altura = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
            'placeholder': 'Altura en cm',
            'min': '0'
        })
    )
    presion_arterial = forms.CharField(
        max_length=20, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
            'placeholder': 'Ej: 120/80'
        })
    )
    alergias = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
            'rows': 4,
            'placeholder': 'Describa las alergias conocidas...'
        })
    )
    medicamentos_actuales = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
            'rows': 4,
            'placeholder': 'Liste los medicamentos actuales...'
        })
    )
    antecedentes_familiares = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
            'rows': 4,
            'placeholder': 'Describa los antecedentes familiares...'
        })
    )
    antecedentes_quirurgicos = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
            'rows': 4,
            'placeholder': 'Describa los antecedentes quirúrgicos...'
        })
    )
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
            'rows': 4,
            'placeholder': 'Observaciones generales...'
        })
    )

    class Meta:
        model = HistorialClinico
        fields = ['paciente', 'grupo_sanguineo', 'alergias_conocidas', 'enfermedades_cronicas']
        widgets = {
            'paciente': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'required': True
            }),
            'grupo_sanguineo': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200'
            }),
            'alergias_conocidas': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'rows': 4,
                'placeholder': 'Describa las alergias conocidas...'
            }),
            'enfermedades_cronicas': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors duration-200',
                'rows': 4,
                'placeholder': 'Describa las enfermedades crónicas...'
            }),
        }

    def save(self, commit=True):
        # Solo guardamos los campos que están en el modelo
        instance = super().save(commit=False)
        
        # Mapear el campo alergias al campo alergias_conocidas del modelo
        if self.cleaned_data.get('alergias'):
            instance.alergias_conocidas = self.cleaned_data['alergias']
        
        if commit:
            instance.save()
        return instance

def historiales_list(request):
    """Lista de historiales clínicos"""
    search = request.GET.get('search', '')
    
    historiales = HistorialClinico.objects.select_related('paciente').all()
    
    if search:
        historiales = historiales.filter(
            Q(paciente__nombre__icontains=search) | 
            Q(paciente__apellido__icontains=search) |
            Q(paciente__rut__icontains=search) |
            Q(grupo_sanguineo__icontains=search)
        )
    
    historiales = historiales.order_by('paciente__apellido', 'paciente__nombre')
    
    paginator = Paginator(historiales, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    total_historiales = HistorialClinico.objects.count()
    
    context = {
        'page_obj': page_obj,
        'historiales': page_obj,
        'is_paginated': page_obj.paginator.num_pages > 1,
        'search': search,
        'total_historiales': total_historiales,
    }
    
    return render(request, 'historiales/list.html', context)

def historiales_detail(request, pk):
    """Detalle de historial clínico"""
    historial = get_object_or_404(HistorialClinico.objects.select_related('paciente'), pk=pk)
    
    context = {
        'historial': historial,
    }
    
    return render(request, 'historiales/detail.html', context)

def historiales_create(request):
    """Crear nuevo historial clínico"""
    if request.method == 'POST':
        form = HistorialForm(request.POST)
        if form.is_valid():
            try:
                historial = form.save()
                messages.success(request, f'Historial clínico creado exitosamente para {historial.paciente.nombre_completo}.')
                return redirect('historiales_detail', pk=historial.pk)
            except Exception as e:
                messages.error(request, f'Error al crear el historial: {str(e)}')
    else:
        form = HistorialForm()
    
    context = {
        'form': form,
        'title': 'Nuevo Historial Clínico',
    }
    
    return render(request, 'historiales/create.html', context)

def historiales_edit(request, pk):
    """Editar historial clínico"""
    historial = get_object_or_404(HistorialClinico, pk=pk)
    
    if request.method == 'POST':
        form = HistorialForm(request.POST, instance=historial)
        if form.is_valid():
            try:
                historial = form.save()
                messages.success(request, f'Historial clínico actualizado exitosamente.')
                return redirect('historiales_detail', pk=historial.pk)
            except Exception as e:
                messages.error(request, f'Error al actualizar el historial: {str(e)}')
    else:
        form = HistorialForm(instance=historial)
    
    context = {
        'form': form,
        'historial': historial,
        'title': 'Editar Historial Clínico',
    }
    
    return render(request, 'historiales/edit.html', context)

@require_http_methods(["POST"])
def historiales_delete(request, pk):
    """Eliminar historial clínico"""
    historial = get_object_or_404(HistorialClinico, pk=pk)
    
    try:
        historial.delete()
        messages.success(request, f'Historial clínico eliminado exitosamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el historial: {str(e)}')
    
    return redirect('historiales_list')
