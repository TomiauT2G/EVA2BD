from django.core.management.base import BaseCommand
from django.db import transaction
from salud_vital.models import (
    Especialidad, Medico, Paciente, ConsultaMedica, 
    Tratamiento, Medicamento, RecetaMedica
)
from datetime import datetime, date, timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Carga datos iniciales para el sistema Salud Vital'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando carga de datos iniciales...'))
        
        with transaction.atomic():
            # Limpiar datos existentes
            self.stdout.write('Limpiando datos existentes...')
            RecetaMedica.objects.all().delete()
            ConsultaMedica.objects.all().delete()
            Tratamiento.objects.all().delete()
            Medicamento.objects.all().delete()
            Medico.objects.all().delete()
            Paciente.objects.all().delete()
            Especialidad.objects.all().delete()
            
            # Crear especialidades
            self.stdout.write('Creando especialidades...')
            especialidades = [
                {'nombre': 'Cardiología', 'descripcion': 'Especialidad médica que se encarga del estudio, diagnóstico y tratamiento de las enfermedades del corazón'},
                {'nombre': 'Neurología', 'descripcion': 'Especialidad médica que trata los trastornos del sistema nervioso'},
                {'nombre': 'Pediatría', 'descripcion': 'Especialidad médica que se centra en la salud y las enfermedades de los niños'},
                {'nombre': 'Ginecología', 'descripcion': 'Especialidad médica que se dedica al cuidado del sistema reproductor femenino'},
                {'nombre': 'Traumatología', 'descripcion': 'Especialidad médica que se dedica al estudio de las lesiones del aparato locomotor'},
            ]
            
            especialidades_objs = []
            for esp_data in especialidades:
                especialidad = Especialidad.objects.create(**esp_data)
                especialidades_objs.append(especialidad)
                self.stdout.write(f'  - {especialidad.nombre}')
            
            # Crear médicos
            self.stdout.write('Creando médicos...')
            medicos_data = [
                {
                    'rut': '12345678-9',
                    'nombre': 'Juan Carlos',
                    'apellido': 'González Pérez',
                    'telefono': '+56912345678',
                    'especialidad': especialidades_objs[0],  # Cardiología
                },
                {
                    'rut': '23456789-0',
                    'nombre': 'María Elena',
                    'apellido': 'Rodríguez Silva',
                    'telefono': '+56923456789',
                    'especialidad': especialidades_objs[1],  # Neurología
                },
                {
                    'rut': '34567890-1',
                    'nombre': 'Pedro Antonio',
                    'apellido': 'Martínez López',
                    'telefono': '+56934567890',
                    'especialidad': especialidades_objs[2],  # Pediatría
                }
            ]
            
            medicos_objs = []
            for medico_data in medicos_data:
                medico = Medico.objects.create(**medico_data)
                medicos_objs.append(medico)
                self.stdout.write(f'  - Dr. {medico.nombre} {medico.apellido}')
            
            # Crear pacientes
            self.stdout.write('Creando pacientes...')
            pacientes_data = [
                {
                    'rut': '11111111-1',
                    'nombre': 'Ana María',
                    'apellido': 'Fernández Castro',
                    'fecha_nacimiento': date(1985, 3, 15),
                    'genero': 'F',
                    'telefono': '+56911111111',
                    'direccion': 'Av. Providencia 1234, Santiago',
                },
                {
                    'rut': '22222222-2',
                    'nombre': 'Carlos Eduardo',
                    'apellido': 'Morales Vega',
                    'fecha_nacimiento': date(1978, 7, 22),
                    'genero': 'M',
                    'telefono': '+56922222222',
                    'direccion': 'Calle Las Condes 567, Las Condes',
                },
                {
                    'rut': '33333333-3',
                    'nombre': 'Sofía Isabel',
                    'apellido': 'Herrera Muñoz',
                    'fecha_nacimiento': date(2010, 12, 8),
                    'genero': 'F',
                    'telefono': '+56933333333',
                    'direccion': 'Pasaje Los Álamos 890, Ñuñoa',
                }
            ]
            
            pacientes_objs = []
            for paciente_data in pacientes_data:
                paciente = Paciente.objects.create(**paciente_data)
                pacientes_objs.append(paciente)
                self.stdout.write(f'  - {paciente.nombre} {paciente.apellido}')
            
            # Crear medicamentos
            self.stdout.write('Creando medicamentos...')
            medicamentos_data = [
                {
                    'nombre': 'Paracetamol',
                    'descripcion': 'Analgésico y antipirético',
                    'precio_unitario': Decimal('1500.00'),
                    'stock': 100,
                    'fecha_vencimiento': date(2025, 12, 31),
                },
                {
                    'nombre': 'Ibuprofeno',
                    'descripcion': 'Antiinflamatorio no esteroideo',
                    'precio_unitario': Decimal('2000.00'),
                    'stock': 75,
                    'fecha_vencimiento': date(2025, 10, 15),
                },
                {
                    'nombre': 'Amoxicilina',
                    'descripcion': 'Antibiótico de amplio espectro',
                    'precio_unitario': Decimal('3500.00'),
                    'stock': 50,
                    'fecha_vencimiento': date(2025, 8, 20),
                }
            ]
            
            medicamentos_objs = []
            for medicamento_data in medicamentos_data:
                medicamento = Medicamento.objects.create(**medicamento_data)
                medicamentos_objs.append(medicamento)
                self.stdout.write(f'  - {medicamento.nombre}')
            
            # Crear consultas médicas
            self.stdout.write('Creando consultas médicas...')
            consultas_data = [
                {
                    'medico': medicos_objs[0],
                    'paciente': pacientes_objs[0],
                    'fecha_consulta': datetime.now() - timedelta(days=5),
                    'motivo': 'Dolor en el pecho y palpitaciones',
                },
                {
                    'medico': medicos_objs[1],
                    'paciente': pacientes_objs[1],
                    'fecha_consulta': datetime.now() - timedelta(days=3),
                    'motivo': 'Dolores de cabeza frecuentes',
                },
                {
                    'medico': medicos_objs[2],
                    'paciente': pacientes_objs[2],
                    'fecha_consulta': datetime.now() - timedelta(days=1),
                    'motivo': 'Control de rutina pediátrico',
                }
            ]
            
            consultas_objs = []
            for consulta_data in consultas_data:
                consulta = ConsultaMedica.objects.create(**consulta_data)
                consultas_objs.append(consulta)
                self.stdout.write(f'  - Consulta {consulta.id}: {consulta.paciente.nombre}')
            
            # Crear tratamientos
            self.stdout.write('Creando tratamientos...')
            tratamientos_data = [
                {
                    'consulta': consultas_objs[0],
                    'descripcion': 'Tratamiento para arritmia cardíaca',
                    'fecha_inicio': date.today(),
                    'fecha_fin': date.today() + timedelta(days=30),
                },
                {
                    'consulta': consultas_objs[1],
                    'descripcion': 'Tratamiento para cefalea tensional',
                    'fecha_inicio': date.today(),
                    'fecha_fin': date.today() + timedelta(days=15),
                }
            ]
            
            tratamientos_objs = []
            for tratamiento_data in tratamientos_data:
                tratamiento = Tratamiento.objects.create(**tratamiento_data)
                tratamientos_objs.append(tratamiento)
                self.stdout.write(f'  - {tratamiento.descripcion}')
            
            # Crear recetas médicas
            self.stdout.write('Creando recetas médicas...')
            recetas_data = [
                {
                    'tratamiento': tratamientos_objs[0],
                    'medicamento': medicamentos_objs[0],
                    'cantidad': 30,
                    'frecuencia': 'cada_8_horas',
                    'duracion': '30 días',
                },
                {
                    'tratamiento': tratamientos_objs[1],
                    'medicamento': medicamentos_objs[1],
                    'cantidad': 20,
                    'frecuencia': 'cada_12_horas',
                    'duracion': '10 días',
                }
            ]
            
            for receta_data in recetas_data:
                receta = RecetaMedica.objects.create(**receta_data)
                self.stdout.write(f'  - Receta: {receta.medicamento.nombre}')
        
        self.stdout.write(
            self.style.SUCCESS('¡Datos iniciales cargados exitosamente!')
        )
        self.stdout.write(
            self.style.WARNING('Credenciales de acceso:')
        )
        self.stdout.write('  Usuario: admin')
        self.stdout.write('  Contraseña: admin123')