from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters
from django.db import models
from datetime import datetime, timedelta

from .models import (
    Especialidad, Medico, Paciente, ConsultaMedica, 
    Tratamiento, Medicamento, RecetaMedica
)
from .serializers import (
    EspecialidadSerializer, MedicoSerializer, PacienteSerializer,
    ConsultaMedicaSerializer, TratamientoSerializer, MedicamentoSerializer,
    RecetaMedicaSerializer, MedicoDetalleSerializer, PacienteDetalleSerializer,
    ConsultaMedicaDetalleSerializer, TratamientoDetalleSerializer
)


# Filtros personalizados
class MedicoFilter(django_filters.FilterSet):
    especialidad = django_filters.CharFilter(field_name='especialidad__nombre', lookup_expr='icontains')
    nombre = django_filters.CharFilter(field_name='nombre', lookup_expr='icontains')
    apellido = django_filters.CharFilter(field_name='apellido', lookup_expr='icontains')
    
    class Meta:
        model = Medico
        fields = ['especialidad', 'nombre', 'apellido']


class PacienteFilter(django_filters.FilterSet):
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
    paciente = django_filters.CharFilter(field_name='paciente__nombre', lookup_expr='icontains')
    medico = django_filters.CharFilter(field_name='medico__nombre', lookup_expr='icontains')
    especialidad = django_filters.CharFilter(field_name='medico__especialidad__nombre', lookup_expr='icontains')
    fecha_desde = django_filters.DateFilter(field_name='fecha_consulta', lookup_expr='gte')
    fecha_hasta = django_filters.DateFilter(field_name='fecha_consulta', lookup_expr='lte')
    
    class Meta:
        model = ConsultaMedica
        fields = ['paciente', 'medico', 'especialidad', 'fecha_desde', 'fecha_hasta']


class MedicamentoFilter(django_filters.FilterSet):
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


# ViewSets
class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'created_at']
    ordering = ['nombre']


class MedicoViewSet(viewsets.ModelViewSet):
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
        consultas = medico.consultamedica_set.all()
        serializer = ConsultaMedicaSerializer(consultas, many=True)
        return Response(serializer.data)


class PacienteViewSet(viewsets.ModelViewSet):
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
        consultas = paciente.consultamedica_set.all()
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
