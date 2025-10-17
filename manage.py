#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

# ============================================================================
# IMPORTACIONES DEL SISTEMA
# ============================================================================
# Módulo para interactuar con el sistema operativo
import os
# Módulo para acceder a argumentos de línea de comandos y funciones del sistema
import sys


# ============================================================================
# FUNCIÓN PRINCIPAL DE ADMINISTRACIÓN
# ============================================================================
def main():
    """
    Ejecuta tareas administrativas de Django.
    
    Esta función es el punto de entrada principal para todas las operaciones
    de gestión de Django como runserver, migrate, collectstatic, etc.
    """
    # Establece el módulo de configuración por defecto si no está definido
    # Esto permite que Django sepa qué archivo de configuración usar
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'salud_vital_project.settings')
    
    try:
        # Importa la función que ejecuta comandos de Django desde la línea de comandos
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Si Django no está instalado o no se puede importar, lanza un error descriptivo
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Ejecuta el comando de Django pasado como argumento en la línea de comandos
    # sys.argv contiene todos los argumentos: ['manage.py', 'comando', 'opciones']
    execute_from_command_line(sys.argv)


# ============================================================================
# PUNTO DE ENTRADA DEL SCRIPT
# ============================================================================
# Solo ejecuta main() si este archivo se ejecuta directamente
# (no cuando se importa como módulo)
if __name__ == '__main__':
    main()
