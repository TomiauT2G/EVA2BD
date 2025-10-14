from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.forms import ModelForm
from django import forms
from django.utils import timezone
from datetime import date, datetime, timedelta

from .models import (
    Especialidad, Medico, Paciente, ConsultaMedica, 
    Tratamiento, Medicamento, RecetaMedica
)


# ModelForms for HTML templates
class EspecialidadForm(ModelForm):
    class Meta:
        model = Especialidad
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Cardiología'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción de la especialidad...'}),
        }

class PacienteForm(ModelForm):
    class Meta:
        model = Paciente
        fields = ['rut', 'nombre', 'apellido', 'fecha_nacimiento', 'telefono', 'direccion']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12.345.678-9'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del paciente'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido del paciente'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dirección completa'}),
        }

class MedicoForm(ModelForm):
    class Meta:
        model = Medico
        fields = ['rut', 'nombre', 'apellido', 'telefono', 'especialidad']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12.345.678-9'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del médico'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido del médico'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
            'especialidad': forms.Select(attrs={'class': 'form-select'}),
        }


# Dashboard View
def dashboard(request):
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
        total_medicos=Count('medico'),
        total_consultas=Count('medico__consultamedica')
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


# ==================== ESPECIALIDADES ====================

def especialidades_list(request):
    """Lista de especialidades"""
    search = request.GET.get('search', '')
    especialidades = Especialidad.objects.all()
    
    if search:
        especialidades = especialidades.filter(
            Q(nombre__icontains=search) | Q(descripcion__icontains=search)
        )
    
    especialidades = especialidades.annotate(
        total_medicos=Count('medico')
    ).order_by('nombre')
    
    paginator = Paginator(especialidades, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
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
    medicos = especialidad.medico_set.all()
    
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


# ==================== PACIENTES ====================

def pacientes_list(request):
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
    
    context = {
        'page_obj': page_obj,
        'search': search,
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
    consultas = paciente.consultamedica_set.select_related(
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
        paciente.delete()
        messages.success(request, f'Paciente "{nombre}" eliminado exitosamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el paciente: {str(e)}')
    
    return redirect('pacientes_list')


# ==================== MÉDICOS ====================

def medicos_list(request):
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
    consultas = medico.consultamedica_set.select_related(
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


# ==================== CONSULTAS MÉDICAS ====================

class ConsultaForm(forms.ModelForm):
    class Meta:
        model = ConsultaMedica
        fields = ['paciente', 'medico', 'fecha_consulta', 'motivo']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'medico': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'fecha_consulta': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local', 'required': True}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'required': True}),
        }


def consultas_list(request):
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


# ==================== TRATAMIENTOS ====================

class TratamientoForm(forms.ModelForm):
    class Meta:
        model = Tratamiento
        fields = ['consulta', 'descripcion', 'fecha_inicio', 'fecha_fin']
        widgets = {
            'consulta': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'required': True}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


def tratamientos_list(request):
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
            messages.success(request, f'Tratamiento "{tratamiento.nombre}" creado exitosamente.')
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
            messages.success(request, f'Tratamiento "{tratamiento.nombre}" actualizado exitosamente.')
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
    nombre = tratamiento.nombre
    
    try:
        tratamiento.delete()
        messages.success(request, f'Tratamiento "{nombre}" eliminado exitosamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el tratamiento: {str(e)}')
    
    return redirect('tratamientos_list')


# ==================== MEDICAMENTOS ====================

class MedicamentoForm(forms.ModelForm):
    class Meta:
        model = Medicamento
        fields = ['nombre', 'descripcion', 'stock', 'precio_unitario', 'fecha_vencimiento']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'required': True}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'required': True}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
        }


def medicamentos_list(request):
    """Lista de medicamentos"""
    search_query = request.GET.get('search', '')
    stock_bajo = request.GET.get('stock_bajo', '')
    vencimiento_proximo = request.GET.get('vencimiento_proximo', '')
    
    medicamentos = Medicamento.objects.all().order_by('nombre')
    
    if search_query:
        medicamentos = medicamentos.filter(
            Q(nombre__icontains=search_query) |
            Q(descripcion__icontains=search_query)
        )
    
    if stock_bajo:
        medicamentos = medicamentos.filter(stock__lt=10)
    
    if vencimiento_proximo:
        from datetime import date, timedelta
        fecha_limite = date.today() + timedelta(days=30)
        medicamentos = medicamentos.filter(fecha_vencimiento__lte=fecha_limite)
    
    paginator = Paginator(medicamentos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'stock_bajo': stock_bajo,
        'vencimiento_proximo': vencimiento_proximo,
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

class RecetaMedicaForm(forms.ModelForm):
    class Meta:
        model = RecetaMedica
        fields = ['tratamiento', 'medicamento', 'cantidad', 'frecuencia', 'duracion']
        widgets = {
            'tratamiento': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'medicamento': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'required': True}),
            'frecuencia': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'duracion': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
        }




def recetas_list(request):
    """Lista de recetas médicas"""
    search_query = request.GET.get('search', '')
    medico_filter = request.GET.get('medico', '')
    medicamento_filter = request.GET.get('medicamento', '')
    
    recetas = RecetaMedica.objects.all().order_by('-id')
    
    if search_query:
        recetas = recetas.filter(
            Q(tratamiento__consulta__paciente__nombre__icontains=search_query) |
            Q(tratamiento__consulta__paciente__apellido__icontains=search_query) |
            Q(tratamiento__consulta__medico__nombre__icontains=search_query) |
            Q(tratamiento__consulta__medico__apellido__icontains=search_query) |
            Q(medicamento__nombre__icontains=search_query)
        )
    
    if medico_filter:
        recetas = recetas.filter(tratamiento__consulta__medico_id=medico_filter)
    
    if medicamento_filter:
        recetas = recetas.filter(medicamento_id=medicamento_filter)
    
    paginator = Paginator(recetas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    medicos = Medico.objects.all()
    medicamentos = Medicamento.objects.all()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'medico_filter': medico_filter,
        'medicamento_filter': medicamento_filter,
        'medicos': medicos,
        'medicamentos': medicamentos,
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
    
    # Obtener medicamentos para el formulario dinámico
    medicamentos = Medicamento.objects.all().order_by('nombre')
    
    context = {
        'form': form,
        'medicamentos': medicamentos,
    }
    
    return render(request, 'recetas/create.html', context)


def recetas_detail(request, pk):
    """Detalle de receta médica"""
    receta = get_object_or_404(
        RecetaMedica.objects.select_related(
            'tratamiento__consulta__paciente',
            'tratamiento__consulta__medico',
            'medicamento'
        ),
        pk=pk
    )
    
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
    
    # Obtener medicamentos para el formulario dinámico
    medicamentos = Medicamento.objects.all().order_by('nombre')
    
    context = {
        'form': form,
        'receta': receta,
        'medicamentos': medicamentos,
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
        messages.error(request, f'Error al eliminar la receta médica: {str(e)}')
    
    return redirect('recetas_list')