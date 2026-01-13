# Changelog - Dashboard de Ventas

## [2.0.0] - 2026-01-13

### ✨ Nuevas Funcionalidades

#### Integración con Supabase
- **Datos históricos 2025**: Migración completa de 31,982 registros de ventas del año 2025 a PostgreSQL (Supabase)
- **Arquitectura híbrida**: 
  - Años ≤ 2025: Consulta desde Supabase (rápido, datos precargados)
  - Años ≥ 2026: Consulta desde Odoo (datos en tiempo real)
- **Mejora de rendimiento**: Carga del dashboard 2025 reducida de ~45s a ~2-3s

#### Mapa Geográfico de Ventas
- **Visualización interactiva**: Mapa de Perú con ventas por departamento
- **Clasificación por penetración**: 
  - 🔴 Baja (< percentil 33)
  - 🟡 Media (percentil 33-66)
  - 🟢 Alta (≥ percentil 66)
- **Tooltips informativos**: Ventas, clientes y ticket promedio por provincia
- **API endpoint**: `/api/mapa-ventas` con routing automático (Supabase/Odoo)

#### Cobertura de Clientes - Estrategia Mixta
- **Cartera base**: Total de clientes activos en Odoo (base histórica completa)
- **Clientes activos 2025**: Clientes que compraron según Supabase
- **Gauge visual**: Indicador de cobertura con umbrales (50%, 65%, 70%)
- **Tabla por canal**: Desglose de cobertura NACIONAL vs total

### 🔧 Mejoras Técnicas

#### Backend
- **Nuevo módulo**: `supabase_manager.py` con funciones de agregación
  - `get_active_partners_count()`: Cuenta clientes únicos por periodo
  - `get_active_partners_by_channel()`: Clientes por canal de ventas
  - `get_sales_by_state()`: Ventas agrupadas por provincia
- **Función Odoo**: `get_total_partners_count()` para cartera completa
- **Routing inteligente**: `get_data_source()` determina fuente según año
- **Normalización de provincias**: Manejo de CALLAO, SAN MARTIN y acentos

#### Frontend
- **JavaScript modular**: Separación de lógica del mapa
- **Variables globales**: `mapaDataGlobal` para acceso desde tooltips
- **Normalización de nombres**: Conversión a mayúsculas para matching consistente
- **ECharts integration**: Registro dinámico de GeoJSON con Peru departamental

#### Base de Datos
- **Tabla Supabase**: `sales_lines` con índices en:
  - `invoice_date` (BRIN)
  - `canal`
  - `partner_id`
  - `provincia`
- **Filtros aplicados**: 
  - `canal != 'INTERNACIONAL'` (antes: `canal = 'NACIONAL'`)
  - Excluye categorías internas (315, 333, 304, 314, 318, 339)
  - Solo facturas posted con default_code

### 🐛 Correcciones

#### Datos
- **Fix filtro de canal**: Cambio de `= 'NACIONAL'` a `!= 'INTERNACIONAL'` para incluir ventas sin canal definido
- **Re-migración 2025**: 31,982 registros ahora coinciden con proyecto de referencia
- **Fechas correctas**: Uso de `año_seleccionado` en lugar de `año_actual` del sistema

#### Mapa
- **Sintaxis JavaScript**: Eliminación de comentarios sin `//` que causaban parse errors
- **Scope de variables**: Uso de global `mapaDataGlobal` para tooltips
- **Normalización**: GeoJSON y datos API usan mayúsculas consistentemente
- **Matching**: Nombres de provincias coinciden entre GeoJSON y datos

#### Cobertura
- **Cartera correcta**: Años históricos usan base total de Odoo, no solo activos del periodo
- **Routing corregido**: `get_data_source(año_seleccionado)` en lugar de `año_actual`
- **Variables KPIs**: Agregadas `cobertura_clientes`, `total_clientes`, `num_clientes_activos` a render_data

### 📝 Documentación
- `SUPABASE_SETUP.md`: Guía completa de migración e índices
- `ESTADO_PROYECTO.md`: Estado actual y decisiones técnicas
- `PROJECT_CONTEXT.md`: Contexto del proyecto y arquitectura

### 🗑️ Limpieza
- Eliminados 25+ scripts de análisis y migración temporal
- Eliminados archivos HTML de documentación obsoletos
- Actualizado `.gitignore` con patrones más completos
- Eliminado caché de desarrollo

### ⚠️ Breaking Changes
Ninguno - La aplicación mantiene retrocompatibilidad con años 2026+

### 📊 Métricas
- **Performance 2025**: ~95% más rápido (45s → 2-3s)
- **Registros Supabase**: 31,982 líneas de venta
- **Provincias con datos**: 21-24 (varía por mes)
- **Cobertura típica**: 2-5% (87 activos / ~3,000 cartera total)

---

## Próximos Pasos Sugeridos
1. ✅ Migrar datos de 2024 a Supabase
2. ✅ Implementar caché Redis para consultas frecuentes
3. ✅ Crear vistas materializadas en Supabase para agregaciones
4. ✅ Agregar filtros interactivos en el mapa (por línea comercial, canal)
5. ✅ Dashboard de análisis de penetración por región
