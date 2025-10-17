# ============================================================================
# SERIALIZADORES PARA API REST - SALUD VITAL
# ============================================================================
# Este archivo define los serializadores de Django REST Framework para
# convertir modelos de Django a JSON y viceversa, incluyendo validaciones

# ============================================================================
# IMPORTACIONES NECESARIAS
# ============================================================================
from rest_framework import serializers
from .models import (
    Especialidad, Medico, Paciente, ConsultaMedica, 
    Tratamiento, Medicamento, RecetaMedica
)

# ============================================================================
# SERIALIZADORES BÁSICOS PARA MODELOS PRINCIPALES
# ============================================================================

class EspecialidadSerializer(serializers.ModelSerializer):
    """Serializador para especialidades médicas con campos básicos"""
    class Meta:
        model = Especialidad
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class MedicoSerializer(serializers.ModelSerializer):
    """Serializador para médicos con campos calculados y validaciones"""
    especialidad_nombre = serializers.CharField(source='especialidad.nombre', read_only=True)
    nombre_completo = serializers.CharField(read_only=True)
    
    class Meta:
        model = Medico
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def validate_rut(self, value):
        """Validación básica del RUT"""
        if len(value) < 8 or len(value) > 12:
            raise serializers.ValidationError("El RUT debe tener entre 8 y 12 caracteres")
        return value


class PacienteSerializer(serializers.ModelSerializer):
    """Serializador para pacientes con campos calculados (edad) y validaciones"""
    nombre_completo = serializers.CharField(read_only=True)
    edad = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Paciente
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def validate_rut(self, value):
        """Validación básica del RUT"""
        if len(value) < 8 or len(value) > 12:
            raise serializers.ValidationError("El RUT debe tener entre 8 y 12 caracteres")
        return value


class ConsultaMedicaSerializer(serializers.ModelSerializer):
    """Serializador para consultas médicas con información relacionada de paciente y médico"""
    paciente_nombre = serializers.CharField(source='paciente.nombre_completo', read_only=True)
    medico_nombre = serializers.CharField(source='medico.nombre_completo', read_only=True)
    especialidad_nombre = serializers.CharField(source='medico.especialidad.nombre', read_only=True)
    
    class Meta:
        model = ConsultaMedica
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class TratamientoSerializer(serializers.ModelSerializer):
    """Serializador para tratamientos con información de paciente/médico y estado calculado"""
    paciente_nombre = serializers.CharField(source='consulta.paciente.nombre_completo', read_only=True)
    medico_nombre = serializers.CharField(source='consulta.medico.nombre_completo', read_only=True)
    esta_activo = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Tratamiento
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class MedicamentoSerializer(serializers.ModelSerializer):
    """Serializador para medicamentos con alertas de stock y vencimiento, incluye validaciones"""
    stock_bajo = serializers.BooleanField(read_only=True)
    proximo_vencimiento = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Medicamento
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def validate_stock(self, value):
        """Validación del stock"""
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo")
        return value

    def validate_precio_unitario(self, value):
        """Validación del precio"""
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0")
        return value


class RecetaMedicaSerializer(serializers.ModelSerializer):
    """Serializador para recetas médicas con cálculo de costo total y validaciones"""
    paciente_nombre = serializers.CharField(source='tratamiento.consulta.paciente.nombre_completo', read_only=True)
    medicamento_nombre = serializers.CharField(source='medicamento.nombre', read_only=True)
    costo_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = RecetaMedica
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def validate_cantidad(self, value):
        """Validación de la cantidad"""
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0")
        return value

# ============================================================================
# SERIALIZADORES DETALLADOS PARA VISTAS ESPECÍFICAS
# ============================================================================
# Serializadores extendidos que incluyen información relacionada para vistas
# de detalle que requieren datos anidados

class ConsultaMedicaDetalleSerializer(ConsultaMedicaSerializer):
    """Serializador detallado para consultas que incluye tratamientos asociados"""
    tratamientos = TratamientoSerializer(source='tratamiento_set', many=True, read_only=True)
    
    class Meta(ConsultaMedicaSerializer.Meta):
        pass


class TratamientoDetalleSerializer(TratamientoSerializer):
    """Serializador detallado para tratamientos que incluye recetas asociadas"""
    recetas = RecetaMedicaSerializer(source='recetamedica_set', many=True, read_only=True)
    
    class Meta(TratamientoSerializer.Meta):
        pass


class MedicoDetalleSerializer(MedicoSerializer):
    """Serializador detallado para médicos que incluye consultas recientes"""
    consultas_recientes = serializers.SerializerMethodField()
    
    class Meta(MedicoSerializer.Meta):
        pass
    
    def get_consultas_recientes(self, obj):
        """Obtiene las últimas 5 consultas del médico en los últimos 30 días"""
        from datetime import datetime, timedelta
        fecha_limite = datetime.now() - timedelta(days=30)
        consultas = obj.consultas_realizadas.filter(fecha_consulta__gte=fecha_limite)[:5]
        return ConsultaMedicaSerializer(consultas, many=True).data


class PacienteDetalleSerializer(PacienteSerializer):
    """Serializador detallado para pacientes que incluye consultas recientes"""
    consultas_recientes = serializers.SerializerMethodField()
    
    class Meta(PacienteSerializer.Meta):
        pass
    
    def get_consultas_recientes(self, obj):
        """Obtiene las últimas 5 consultas del paciente"""
        consultas = obj.consultas.all()[:5]
        return ConsultaMedicaSerializer(consultas, many=True).data