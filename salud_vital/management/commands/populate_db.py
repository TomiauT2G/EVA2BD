from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from salud_vital.models import (
    Especialidad, Medico, Paciente, HistorialClinico, 
    CitaMedica, ConsultaMedica, Medicamento, Tratamiento, RecetaMedica
)

class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de prueba'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando población de la base de datos...'))
        
        # Crear especialidades
        especialidades_data = [
            'Cardiología',
            'Neurología', 
            'Pediatría',
            'Ginecología',
            'Traumatología',
            'Dermatología',
            'Psiquiatría',
            'Oftalmología',
            'Otorrinolaringología',
            'Endocrinología'
        ]
        
        especialidades = []
        for nombre in especialidades_data:
            especialidad, created = Especialidad.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': f'Especialidad médica en {nombre}'}
            )
            especialidades.append(especialidad)
            if created:
                self.stdout.write(f'Especialidad creada: {nombre}')
        
        # Crear médicos
        medicos_data = [
            {
                'nombre': 'Dr. Carlos',
                'apellido': 'Rodríguez Mendoza',
                'rut': '12345678-9',
                'telefono': '+56912345678',
                'email': 'carlos.rodriguez@saludvital.com',
                'especialidad': especialidades[0]  # Cardiología
            },
            {
                'nombre': 'Dra. María',
                'apellido': 'González Silva',
                'rut': '23456789-0',
                'telefono': '+56923456789',
                'email': 'maria.gonzalez@saludvital.com',
                'especialidad': especialidades[1]  # Neurología
            },
            {
                'nombre': 'Dr. José',
                'apellido': 'Martínez López',
                'rut': '34567890-1',
                'telefono': '+56934567890',
                'email': 'jose.martinez@saludvital.com',
                'especialidad': especialidades[2]  # Pediatría
            },
            {
                'nombre': 'Dra. Ana',
                'apellido': 'Fernández Castro',
                'rut': '45678901-2',
                'telefono': '+56945678901',
                'email': 'ana.fernandez@saludvital.com',
                'especialidad': especialidades[3]  # Ginecología
            },
            {
                'nombre': 'Dr. Luis',
                'apellido': 'Pérez Morales',
                'rut': '56789012-3',
                'telefono': '+56956789012',
                'email': 'luis.perez@saludvital.com',
                'especialidad': especialidades[4]  # Traumatología
            }
        ]
        
        medicos = []
        for data in medicos_data:
            medico, created = Medico.objects.get_or_create(
                rut=data['rut'],
                defaults=data
            )
            medicos.append(medico)
            if created:
                self.stdout.write(f'Médico creado: {data["nombre"]} {data["apellido"]}')
        
        # Crear pacientes
        pacientes_data = [
            {
                'nombre': 'Juan Carlos',
                'apellido': 'Sánchez Herrera',
                'rut': '11111111-1',
                'fecha_nacimiento': '1985-03-15',
                'telefono': '+56911111111',
                'email': 'juan.sanchez@email.com',
                'direccion': 'Av. Providencia 1234, Santiago'
            },
            {
                'nombre': 'María Elena',
                'apellido': 'Torres Vega',
                'rut': '22222222-2',
                'fecha_nacimiento': '1990-07-22',
                'telefono': '+56922222222',
                'email': 'maria.torres@email.com',
                'direccion': 'Calle Las Condes 567, Las Condes'
            },
            {
                'nombre': 'Pedro Antonio',
                'apellido': 'Ramírez Díaz',
                'rut': '33333333-3',
                'fecha_nacimiento': '1978-11-08',
                'telefono': '+56933333333',
                'email': 'pedro.ramirez@email.com',
                'direccion': 'Pasaje Los Álamos 890, Ñuñoa'
            },
            {
                'nombre': 'Carmen Gloria',
                'apellido': 'Muñoz Contreras',
                'rut': '44444444-4',
                'fecha_nacimiento': '1995-01-30',
                'telefono': '+56944444444',
                'email': 'carmen.munoz@email.com',
                'direccion': 'Av. Vicuña Mackenna 2345, Macul'
            },
            {
                'nombre': 'Roberto Carlos',
                'apellido': 'Jiménez Rojas',
                'rut': '55555555-5',
                'fecha_nacimiento': '1982-09-12',
                'telefono': '+56955555555',
                'email': 'roberto.jimenez@email.com',
                'direccion': 'Calle San Martín 678, Valparaíso'
            },
            {
                'nombre': 'Francisca Isabel',
                'apellido': 'Vargas Soto',
                'rut': '66666666-6',
                'fecha_nacimiento': '1988-05-18',
                'telefono': '+56966666666',
                'email': 'francisca.vargas@email.com',
                'direccion': 'Av. Libertador 1567, Viña del Mar'
            }
        ]
        
        pacientes = []
        for data in pacientes_data:
            paciente, created = Paciente.objects.get_or_create(
                rut=data['rut'],
                defaults=data
            )
            pacientes.append(paciente)
            if created:
                self.stdout.write(f'Paciente creado: {data["nombre"]} {data["apellido"]}')
        
        # Crear historiales clínicos
        grupos_sanguineos = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        for i, paciente in enumerate(pacientes):
            historial, created = HistorialClinico.objects.get_or_create(
                paciente=paciente,
                defaults={
                    'grupo_sanguineo': grupos_sanguineos[i % len(grupos_sanguineos)],
                    'alergias_conocidas': 'Ninguna conocida' if i % 2 == 0 else 'Alergia a penicilina, mariscos',
                    'enfermedades_cronicas': 'Diabetes tipo 2' if i % 3 == 0 else 'Hipertensión arterial' if i % 3 == 1 else 'Ninguna'
                }
            )
            if created:
                self.stdout.write(f'Historial clínico creado para: {paciente.nombre} {paciente.apellido}')
        
        # Crear medicamentos
        from datetime import date
        medicamentos_data = [
            {
                'nombre': 'Paracetamol 500mg',
                'descripcion': 'Analgésico y antipirético en tabletas de 500mg',
                'stock': 100,
                'precio_unitario': 150.00,
                'fecha_vencimiento': date.today() + timedelta(days=365)
            },
            {
                'nombre': 'Ibuprofeno 400mg',
                'descripcion': 'Antiinflamatorio no esteroideo en cápsulas de 400mg',
                'stock': 75,
                'precio_unitario': 200.00,
                'fecha_vencimiento': date.today() + timedelta(days=300)
            },
            {
                'nombre': 'Amoxicilina 500mg',
                'descripcion': 'Antibiótico de amplio espectro en cápsulas de 500mg',
                'stock': 50,
                'precio_unitario': 350.00,
                'fecha_vencimiento': date.today() + timedelta(days=180)
            },
            {
                'nombre': 'Losartán 50mg',
                'descripcion': 'Antihipertensivo en comprimidos de 50mg',
                'stock': 90,
                'precio_unitario': 250.00,
                'fecha_vencimiento': date.today() + timedelta(days=500)
            },
            {
                'nombre': 'Metformina 850mg',
                'descripcion': 'Antidiabético en comprimidos de 850mg',
                'stock': 65,
                'precio_unitario': 300.00,
                'fecha_vencimiento': date.today() + timedelta(days=600)
            },
            {
                'nombre': 'Omeprazol 20mg',
                'descripcion': 'Inhibidor de la bomba de protones en cápsulas de 20mg',
                'stock': 60,
                'precio_unitario': 280.00,
                'fecha_vencimiento': date.today() + timedelta(days=400)
            }
        ]
        
        medicamentos = []
        for data in medicamentos_data:
            medicamento, created = Medicamento.objects.get_or_create(
                nombre=data['nombre'],
                defaults=data
            )
            medicamentos.append(medicamento)
            if created:
                self.stdout.write(f'Medicamento creado: {medicamento.nombre}')
        
        # Crear citas médicas
        base_date = timezone.now()
        for i in range(8):
            fecha_hora_cita = base_date + timedelta(days=i*3, hours=9+i)
            
            cita, created = CitaMedica.objects.get_or_create(
                paciente=pacientes[i % len(pacientes)],
                medico=medicos[i % len(medicos)],
                fecha_hora_cita=fecha_hora_cita,
                defaults={
                    'motivo': f'Consulta de control {i+1}',
                    'observaciones': f'Paciente solicita revisión general. Cita #{i+1}',
                    'estado': 'Programada' if i < 4 else 'Realizada'
                }
            )
            if created:
                self.stdout.write(f'Cita médica creada: {fecha_hora_cita.strftime("%d/%m/%Y %H:%M")} - {pacientes[i % len(pacientes)].nombre}')
        
        # Crear consultas médicas
        for i in range(6):
            fecha_consulta = base_date - timedelta(days=i*5)
            
            consulta, created = ConsultaMedica.objects.get_or_create(
                paciente=pacientes[i % len(pacientes)],
                medico=medicos[i % len(medicos)],
                fecha_consulta=fecha_consulta,
                defaults={
                    'motivo': f'Dolor abdominal' if i % 3 == 0 else f'Control rutinario' if i % 3 == 1 else 'Seguimiento tratamiento',
                    'diagnostico': f'Diagnóstico para consulta {i+1}. Paciente presenta síntomas que requieren seguimiento médico.'
                }
            )
            if created:
                self.stdout.write(f'Consulta médica creada: {fecha_consulta.strftime("%d/%m/%Y")} - {pacientes[i % len(pacientes)].nombre}')
        
        # Crear tratamientos y recetas
        consultas = list(ConsultaMedica.objects.all())
        for i, consulta in enumerate(consultas[:4]):  # Solo para las primeras 4 consultas
            fecha_inicio = consulta.fecha_consulta.date()
            fecha_fin = fecha_inicio + timedelta(days=30 + (i * 15))
            
            tratamiento, created = Tratamiento.objects.get_or_create(
                consulta=consulta,
                defaults={
                    'descripcion': f'Tratamiento para {consulta.diagnostico}. Tomar medicación según indicaciones médicas.',
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin
                }
            )
            if created:
                self.stdout.write(f'Tratamiento creado para consulta: {consulta.id}')
                
                # Crear receta para el tratamiento
                receta, receta_created = RecetaMedica.objects.get_or_create(
                    tratamiento=tratamiento,
                    medicamento=medicamentos[i % len(medicamentos)],
                    defaults={
                        'cantidad': 30 + (i * 10),
                        'frecuencia': 'Cada 8 horas' if i % 2 == 0 else 'Cada 12 horas',
                        'duracion': f'{7 + (i * 3)} días'
                    }
                )
                
                if receta_created:
                    self.stdout.write(f'Receta creada: {medicamentos[i % len(medicamentos)].nombre}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n¡Base de datos poblada exitosamente!\n'
                f'- {len(especialidades)} especialidades\n'
                f'- {len(medicos)} médicos\n'
                f'- {len(pacientes)} pacientes\n'
                f'- {len(pacientes)} historiales clínicos\n'
                f'- {len(medicamentos)} medicamentos\n'
                f'- {CitaMedica.objects.count()} citas médicas\n'
                f'- {ConsultaMedica.objects.count()} consultas médicas\n'
                f'- {Tratamiento.objects.count()} tratamientos\n'
                f'- {RecetaMedica.objects.count()} recetas médicas\n'
            )
        )