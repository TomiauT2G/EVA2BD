# ============================================================================
# IMPORTACIONES NECESARIAS
# ============================================================================
# Importación del módulo de modelos de Django para definir las entidades de la base de datos
# Importación de date y timedelta para manejo de fechas y cálculos temporales
from django.db import models
from datetime import date, timedelta


# ============================================================================
# MODELO ESPECIALIDAD
# ============================================================================
# Define las especialidades médicas disponibles en el sistema
# Cada especialidad puede tener múltiples médicos asociados
class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'especialidades'
        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# ============================================================================
# MODELO MÉDICO
# ============================================================================
# Define la información de los médicos del sistema
# Cada médico está asociado a una especialidad y puede atender múltiples pacientes
class Medico(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    activo = models.BooleanField(default=True)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.PROTECT, related_name='medicos')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medicos'
        verbose_name = 'Médico'
        verbose_name_plural = 'Médicos'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"Dr. {self.nombre} {self.apellido}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


# ============================================================================
# MODELO PACIENTE
# ============================================================================
# Define la información básica de los pacientes del sistema
# Incluye datos personales y de contacto, con cálculo automático de edad
class Paciente(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pacientes'
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def edad(self):
        today = date.today()
        return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))


# ============================================================================
# MODELO HISTORIAL CLÍNICO
# ============================================================================
# Almacena la información médica básica de cada paciente
# Relación uno a uno con el paciente, incluye grupo sanguíneo, alergias y enfermedades crónicas
class HistorialClinico(models.Model):
    TIPO_SANGRE_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, related_name='historial_clinico')
    grupo_sanguineo = models.CharField(max_length=5, choices=TIPO_SANGRE_CHOICES, blank=True, null=True)
    alergias_conocidas = models.TextField(blank=True, null=True)
    enfermedades_cronicas = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'historiales_clinicos'
        verbose_name = 'Historial Clínico'
        verbose_name_plural = 'Historiales Clínicos'

    def __str__(self):
        return f"Historial de {self.paciente.nombre_completo}"


# ============================================================================
# MODELO CITA MÉDICA
# ============================================================================
# Gestiona las citas programadas entre pacientes y médicos
# Incluye estados de seguimiento y información adicional sobre la cita
class CitaMedica(models.Model):
    ESTADO_CHOICES = [
        ('Programada', 'Programada'),
        ('Confirmada', 'Confirmada'),
        ('Cancelada', 'Cancelada'),
        ('Realizada', 'Realizada'),
    ]
    
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, related_name='citas')
    medico = models.ForeignKey(Medico, on_delete=models.PROTECT, related_name='citas')
    fecha_hora_cita = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Programada')
    motivo = models.TextField(blank=True, null=True, help_text="Motivo de la cita médica")
    observaciones = models.TextField(blank=True, null=True, help_text="Observaciones adicionales")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'citas_medicas'
        verbose_name = 'Cita Médica'
        verbose_name_plural = 'Citas Médicas'
        ordering = ['-fecha_hora_cita']

    def __str__(self):
        return f"Cita {self.paciente.nombre_completo} - {self.fecha_hora_cita.strftime('%d/%m/%Y %H:%M')}"


# ============================================================================
# MODELO CONSULTA MÉDICA
# ============================================================================
# Registra las consultas médicas realizadas
# Puede estar asociada a una cita previa o ser una consulta de emergencia
class ConsultaMedica(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, related_name='consultas')
    medico = models.ForeignKey(Medico, on_delete=models.PROTECT, related_name='consultas_realizadas')
    cita = models.ForeignKey(CitaMedica, on_delete=models.SET_NULL, null=True, blank=True, related_name='consulta_generada')
    fecha_consulta = models.DateTimeField()
    motivo = models.TextField()
    diagnostico = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'consultas_medicas'
        verbose_name = 'Consulta Médica'
        verbose_name_plural = 'Consultas Médicas'
        ordering = ['-fecha_consulta']

    def __str__(self):
        return f"Consulta {self.paciente.nombre_completo} - {self.fecha_consulta.strftime('%d/%m/%Y')}"


# ============================================================================
# MODELO TRATAMIENTO
# ============================================================================
# Define los tratamientos médicos prescritos en las consultas
# Incluye fechas de inicio y fin, con propiedades para verificar estado y duración
class Tratamiento(models.Model):
    consulta = models.ForeignKey(ConsultaMedica, on_delete=models.CASCADE, related_name='tratamientos')
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tratamientos'
        verbose_name = 'Tratamiento'
        verbose_name_plural = 'Tratamientos'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"Tratamiento {self.consulta.paciente.nombre_completo} - {self.fecha_inicio}"

    @property
    def esta_activo(self):
        return date.today() <= self.fecha_fin

    @property
    def duracion_dias(self):
        return (self.fecha_fin - self.fecha_inicio).days


# ============================================================================
# MODELO MEDICAMENTO
# ============================================================================
# Catálogo de medicamentos disponibles en el sistema
# Incluye control de stock, precios y fechas de vencimiento con alertas automáticas
class Medicamento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_vencimiento = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medicamentos'
        verbose_name = 'Medicamento'
        verbose_name_plural = 'Medicamentos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def stock_bajo(self):
        return self.stock <= 10

    @property
    def proximo_vencimiento(self):
        return self.fecha_vencimiento <= date.today() + timedelta(days=30)


# ============================================================================
# MODELO RECETA MÉDICA
# ============================================================================
# Relaciona los tratamientos con los medicamentos prescritos
# Incluye cantidad, frecuencia, duración y cálculo automático del costo total
class RecetaMedica(models.Model):
    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.CASCADE, related_name='recetas')
    medicamento = models.ForeignKey(Medicamento, on_delete=models.PROTECT, related_name='recetas')
    cantidad = models.PositiveIntegerField()
    frecuencia = models.CharField(max_length=50)
    duracion = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recetas_medicas'
        verbose_name = 'Receta Médica'
        verbose_name_plural = 'Recetas Médicas'
        ordering = ['-created_at']

    def __str__(self):
        return f"Receta {self.medicamento.nombre} - {self.tratamiento.consulta.paciente.nombre_completo}"

    @property
    def costo_total(self):
        return self.cantidad * self.medicamento.precio_unitario
