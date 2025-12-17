#!/usr/bin/env python3
"""
Script para limpiar el caché del dashboard.
Uso: python limpiar_cache.py [año] [mes]
     python limpiar_cache.py --all    # Limpia todo el caché
"""

import os
import sys
import shutil

CACHE_DIR = os.path.join(os.path.dirname(__file__), '__pycache__', 'dashboard_cache')

def limpiar_cache_mes(año, mes):
    """Limpia el caché de un mes específico."""
    cache_key = f"dashboard_data_{año}_{mes:02d}"
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.pkl")
    
    if os.path.exists(cache_file):
        os.remove(cache_file)
        print(f"✅ Caché eliminado para {año}-{mes:02d}")
        return True
    else:
        print(f"⚠️ No existe caché para {año}-{mes:02d}")
        return False

def limpiar_todo_cache():
    """Limpia todo el directorio de caché."""
    if os.path.exists(CACHE_DIR):
        archivos = [f for f in os.listdir(CACHE_DIR) if f.endswith('.pkl')]
        if archivos:
            for archivo in archivos:
                os.remove(os.path.join(CACHE_DIR, archivo))
            print(f"✅ Eliminados {len(archivos)} archivos de caché")
        else:
            print("ℹ️ No hay archivos de caché para eliminar")
    else:
        print("ℹ️ El directorio de caché no existe")

def listar_cache():
    """Lista todos los archivos de caché existentes."""
    if os.path.exists(CACHE_DIR):
        archivos = [f for f in os.listdir(CACHE_DIR) if f.endswith('.pkl')]
        if archivos:
            print(f"📁 Archivos de caché encontrados ({len(archivos)}):")
            for archivo in sorted(archivos):
                # Extraer año y mes del nombre del archivo
                partes = archivo.replace('dashboard_data_', '').replace('.pkl', '').split('_')
                if len(partes) == 2:
                    año, mes = partes
                    tamaño = os.path.getsize(os.path.join(CACHE_DIR, archivo))
                    print(f"  - {año}-{mes}: {tamaño:,} bytes")
        else:
            print("ℹ️ No hay archivos de caché")
    else:
        print("ℹ️ El directorio de caché no existe")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print(__doc__)
        listar_cache()
    elif len(sys.argv) == 2 and sys.argv[1] == '--all':
        limpiar_todo_cache()
    elif len(sys.argv) == 2 and sys.argv[1] == '--list':
        listar_cache()
    elif len(sys.argv) == 3:
        try:
            año = int(sys.argv[1])
            mes = int(sys.argv[2])
            if 1 <= mes <= 12:
                limpiar_cache_mes(año, mes)
            else:
                print("❌ El mes debe estar entre 1 y 12")
        except ValueError:
            print("❌ Año y mes deben ser números")
            print(__doc__)
    else:
        print(__doc__)
