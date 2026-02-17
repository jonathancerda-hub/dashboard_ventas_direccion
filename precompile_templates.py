#!/usr/bin/env python
"""
Pre-compila templates de Jinja2 para evitar timeout en Render Free
Se ejecuta durante el buildCommand, antes de iniciar gunicorn
"""
import os
import sys

# Asegurarse que estamos en el directorio correcto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Flag para indicar que solo queremos compilar templates, no conectar a servicios
os.environ['PRECOMPILING_TEMPLATES'] = 'true'

print("🔧 Pre-compilando templates Jinja2...")

try:
    from jinja2 import FileSystemBytecodeCache
    from flask import Flask
    
    # Crear app mínima solo para compilar templates
    app = Flask(__name__)
    app.secret_key = 'precompile-key-temporary'
    
    # Configurar bytecode cache
    bytecode_cache_dir = os.path.join(os.path.dirname(__file__), '__pycache__', 'jinja2_cache')
    os.makedirs(bytecode_cache_dir, exist_ok=True)
    app.jinja_env.bytecode_cache = FileSystemBytecodeCache(bytecode_cache_dir)
    
    # Lista de templates a pre-compilar
    templates = [
        'base.html',
        'dashboard_clean.html',
        'login.html',
        'sales.html'
    ]
    
    compiled_count = 0
    for template_name in templates:
        try:
            print(f"  📄 Compilando {template_name}...", end=' ', flush=True)
            # Compilar template (esto lo guarda en el bytecode cache)
            template = app.jinja_env.get_template(template_name)
            print("✅")
            compiled_count += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            # No fallar el build por templates opcionales
            if template_name == 'dashboard_clean.html':
                print(f"⚠️ Error crítico compilando {template_name}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
    
    print(f"✅ Pre-compilados {compiled_count}/{len(templates)} templates")
    print(f"📦 Cache guardado en: {bytecode_cache_dir}")
    
    # Verificar que los archivos se crearon
    cache_files = os.listdir(bytecode_cache_dir) if os.path.exists(bytecode_cache_dir) else []
    print(f"📁 Archivos en cache: {len(cache_files)}")
    
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Error durante pre-compilación: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
