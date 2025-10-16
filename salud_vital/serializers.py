from rest_framework import serializers
from .models import (
    Especialidad, Medico, Paciente, ConsultaMedica, 
    Tratamiento, Medicamento, RecetaMedica
)


class EspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class MedicoSerializer(serializers.ModelSerializer):
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
    paciente_nombre = serializers.CharField(source='paciente.nombre_completo', read_only=True)
    medico_nombre = serializers.CharField(source='medico.nombre_completo', read_only=True)
    especialidad_nombre = serializers.CharField(source='medico.especialidad.nombre', read_only=True)
    
    class Meta:
        model = ConsultaMedica
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class TratamientoSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.CharField(source='consulta.paciente.nombre_completo', read_only=True)
    medico_nombre = serializers.CharField(source='consulta.medico.nombre_completo', read_only=True)
    esta_activo = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Tratamiento
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class MedicamentoSerializer(serializers.ModelSerializer):
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


# Serializers detallados para vistas específicas
class ConsultaMedicaDetalleSerializer(ConsultaMedicaSerializer):
    tratamientos = TratamientoSerializer(source='tratamiento_set', many=True, read_only=True)
    
    class Meta(ConsultaMedicaSerializer.Meta):
        pass


class TratamientoDetalleSerializer(TratamientoSerializer):
    recetas = RecetaMedicaSerializer(source='recetamedica_set', many=True, read_only=True)
    
    class Meta(TratamientoSerializer.Meta):
        pass


class MedicoDetalleSerializer(MedicoSerializer):
    consultas_recientes = serializers.SerializerMethodField()
    
    class Meta(MedicoSerializer.Meta):
        pass
    
    def get_consultas_recientes(self, obj):
        from datetime import datetime, timedelta
        fecha_limite = datetime.now() - timedelta(days=30)
        consultas = obj.consultamedica_set.filter(fecha_consulta__gte=fecha_limite)[:5]
        return ConsultaMedicaSerializer(consultas, many=True).data


class PacienteDetalleSerializer(PacienteSerializer):
    consultas_recientes = serializers.SerializerMethodField()
    
    class Meta(PacienteSerializer.Meta):
        pass
    
    def get_consultas_recientes(self, obj):
        consultas = obj.consultas.all()[:5]
        return ConsultaMedicaSerializer(consultas, many=True).data