from django.db import models
from datetime import date, timedelta


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


class HistorialClinico(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, related_name='historial_clinico')
    grupo_sanguineo = models.CharField(max_length=5, blank=True, null=True)
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
