# 📊 ESTADO ACTUAL DEL PROYECTO - Dashboard Dirección de Ventas

**Fecha:** 13 de enero de 2026  
**Estado General:** ✅ Funcional con Supabase integrado  
**Última Actualización:** Migración completa 2025 (31,982 registros)

---

## 🎯 GRÁFICOS IMPLEMENTADOS

### ✅ **1. KPIs Principales** (Superior del Dashboard)
- **Meta Total**: Comparación vs objetivo mensual
- **Venta Total**: Ventas totales del período
- **% Avance**: Porcentaje de cumplimiento
- **Meta/Venta IPN**: Indicadores de Introducción Productos Nuevos
- **Ubicación:** Fila superior, tarjetas grandes
- **Tecnología:** HTML/CSS estático

### ✅ **2. Tabla de Avance por Línea Comercial**
- **Descripción:** Muestra meta, venta real, diferencia y % cumplimiento por línea
- **Líneas:** AGROVET, MONTANA, BIOMONT, SOLVET, VIMIFOS, GLOBAL, NUTRAL, HIPRA
- **Ubicación:** Debajo de KPIs principales
- **Formato:** Tabla interactiva con colores según cumplimiento

### ✅ **3. Análisis de Clientes por Línea Comercial**
- **Métricas:**
  - S/ Facturado por línea
  - N° Clientes únicos
  - Ticket/Cliente promedio
- **Ubicación:** Lado derecho de tabla de avance
- **Formato:** Tabla

### ✅ **4. Gauge de Cobertura de Clientes** (SVG Animado)
- **Métrica Principal:** % de clientes activos vs cartera total
- **Diseño:** Gauge circular con gradiente de colores
- **Rangos:**
  - 0-50%: Crítico (rojo)
  - 50-65%: Aceptable (naranja)
  - 65-70%: Bueno (amarillo)
  - 70%+: Excelente (verde)
- **Tecnología:** SVG puro con animaciones CSS
- **Ubicación:** Sección de Cobertura, columna izquierda

### ✅ **5. Indicadores de Cobertura** (Grid 2x2)
- **Métricas:**
  - Total Clientes en Cartera
  - Clientes Activos
  - Clientes Inactivos
  - % Cobertura General
- **Diseño:** Tarjetas con iconos y colores diferenciados
- **Ubicación:** Junto al gauge de cobertura

### ✅ **6. Top 5 Productos Más Vendidos**
- **Métricas:**
  - Nombre del producto
  - Unidades vendidas
  - Monto total (S/)
- **Diseño:** Barras horizontales con colores degradados
- **Ubicación:** Sección de productos, columna izquierda
- **Tecnología:** HTML/CSS con animaciones

### ✅ **7. Análisis de Ciclo de Vida de Productos** (ECharts)
- **Categorías:**
  - NUEVO LANZAMIENTO (verde claro): Lanzados recientemente
  - REGULAR (verde): Productos estándar en catálogo
  - VIEJO (naranja): Próximos a discontinuar
- **Métricas:** Monto de ventas por categoría
- **Tipo:** Gráfico de barras apiladas (stacked bar)
- **Tecnología:** ECharts
- **Ubicación:** Sección de productos, columna derecha

### ✅ **8. Tendencia Histórica 12 Meses** (Chart.js)
- **Descripción:** Evolución de ventas vs metas durante todo el año seleccionado
- **Datos:**
  - Línea azul: Ventas reales
  - Línea verde punteada: Meta mensual
  - Áreas sombreadas: Sobre/bajo cumplimiento
- **Características:**
  - SIEMPRE muestra 12 meses completos del año seleccionado
  - NO depende del filtro de mes individual
  - Fuente de datos: Supabase para años ≤2025, Odoo para años ≥2026
- **Tecnología:** Chart.js (line chart)
- **Ubicación:** Sección central amplia

### ✅ **9. Análisis RFM - Segmentación de Clientes** (2 paneles)

#### Panel 1: Distribución por Segmento (Chart.js Doughnut)
- **Segmentos:**
  - 🟢 Campeones: Compran frecuente y recientemente, alto valor
  - 🟢 Leales: Compran regularmente, buen valor
  - 🟢 Potenciales: Compras recientes, pueden crecer
  - 🔵 Nuevos: Primera compra reciente
  - 🟡 En Riesgo: Buenos clientes sin compras recientes
  - 🟠 Hibernando: Bajo valor, inactivos
  - 🔴 Perdidos: Mucho tiempo sin comprar
- **Tecnología:** Chart.js (doughnut chart)
- **Ubicación:** Análisis RFM, columna izquierda

#### Panel 2: Top 20 Clientes por Valor
- **Columnas:**
  - # Ranking
  - Cliente (nombre)
  - Segmento RFM
  - Recency (días desde última compra)
  - Frequency (número de pedidos)
  - Valor Monetario (S/)
- **Formato:** Tabla scrolleable con colores por segmento
- **Ubicación:** Análisis RFM, columna derecha

### ✅ **10. Selector de Año y Mes**
- **Funcionalidad:**
  - Dropdown de año: 2020 - presente
  - Dropdown de mes: Enero - Diciembre
  - Botón calendario interactivo
- **Ubicación:** Header del dashboard
- **Comportamiento:** Recarga dashboard con datos filtrados

---

## 🚧 GRÁFICOS PENDIENTES (Según PRD)

### ⏳ **1. Heatmap de Actividad de Ventas** (CÓDIGO EXISTE, NO VISIBLE)
- **Estado:** Backend implementado en app.py (líneas 855-902), pero NO renderizado en HTML
- **Descripción:** Matriz de día de semana × semana del mes mostrando actividad de ventas
- **Propósito:** Identificar patrones de comportamiento (días/semanas más activos)
- **Tecnología Sugerida:** Chart.js Matrix o ECharts Heatmap
- **Datos Disponibles:** `heatmap_data` ya se calcula en backend

### ⏳ **2. Análisis Geográfico - Mapa de Provincias**
- **Estado:** Backend parcialmente implementado, NO visible en frontend
- **Descripción:** Mapa de Perú con ventas por provincia/departamento
- **Métricas:**
  - Ventas por provincia
  - Número de clientes por zona
  - Heat map de concentración
- **Tecnología Sugerida:** Leaflet.js o ECharts Map
- **Datos Disponibles:** Campo `provincia` y `zona` en datos

### ⏳ **3. Frecuencia de Compra**
- **Métrica:** Pedidos promedio por cliente/mes
- **Meta:** ≥2.0 (estándar industria: 2-3)
- **Fórmula:** Total pedidos / Total clientes activos
- **Estado:** NO implementado
- **Prioridad:** ALTA (KPI principal según PRD)

### ⏳ **4. Ticket Promedio - Tendencia Mensual**
- **Métrica:** Evolución del valor promedio por transacción
- **Meta:** Crecimiento mensual ≥5%
- **Fórmula:** Ventas totales / Número de facturas
- **Estado:** NO implementado (solo se calcula por línea comercial)
- **Prioridad:** ALTA (KPI principal según PRD)

### ⏳ **5. Ventas por Canal - Distribución**
- **Descripción:** Gráfico de pastel o barras mostrando % por canal
- **Canales:** NACIONAL, EXPORTACIÓN, ECOMMERCE, etc.
- **Meta:** Balance según estrategia (Digital: 20%, Oficina: 15%, eCommerce: 65%)
- **Estado:** Datos disponibles en campo `canal`, NO visualizado
- **Prioridad:** MEDIA

### ⏳ **6. Performance por Vendedor**
- **Métricas:**
  - Ranking de vendedores por ventas
  - % cumplimiento individual
  - Tendencia mensual
- **Estado:** Datos disponibles en campo `vendedor`, NO visualizado
- **Prioridad:** ALTA (importante para dirección)

### ⏳ **7. Análisis de Productos - Top/Bottom Performers**
- **Descripción:** 
  - Top 20 productos con mayor crecimiento
  - Bottom 10 productos con caída
  - Productos sin movimiento
- **Estado:** Solo implementado Top 5, falta análisis completo
- **Prioridad:** MEDIA

### ⏳ **8. Tasa de Conversión** (Cotizaciones → Ventas)
- **Métrica:** % cotizaciones convertidas en ventas
- **Meta:** ≥30%
- **Fórmula:** (Ventas cerradas / Cotizaciones) × 100
- **Estado:** NO implementado, requiere data de cotizaciones
- **Prioridad:** BAJA (requiere datos adicionales de Odoo)

### ⏳ **9. Ciclo de Venta**
- **Métrica:** Días promedio desde contacto hasta cierre
- **Meta:** ≤21 días
- **Estado:** NO implementado
- **Prioridad:** BAJA

### ⏳ **10. Alertas y Notificaciones**
- **Funcionalidad:** Sistema de alertas automáticas cuando:
  - Cobertura cae bajo 60%
  - Vendedor bajo 70% de meta
  - Cliente clave sin compras por 60+ días
- **Estado:** NO implementado
- **Prioridad:** MEDIA

---

## 🔧 ARQUITECTURA TÉCNICA ACTUAL

### **Backend**
- **Framework:** Flask 3.1.1
- **Base de Datos Principal:** Odoo XML-RPC (amah.odoo.com)
- **Base de Datos Histórica:** Supabase PostgreSQL
  - 31,982 registros de 2025 migrados
  - Años ≤2025: Supabase (optimizado para Render.com 512MB RAM)
  - Años ≥2026: Odoo en tiempo real
- **Gestión de Metas:** Google Sheets API
- **Cache:** Sistema de archivos .pkl (dashboard_cache/)
- **Python:** 3.13.7

### **Frontend**
- **Template Engine:** Jinja2
- **Gráficos:**
  - Chart.js: Líneas, barras, doughnut
  - ECharts: Ciclo de vida de productos
  - SVG + CSS: Gauge de cobertura
- **Componentes UI:** Bootstrap Icons, Flatpickr

### **Filtros Aplicados en Datos**
```python
# odoo_manager.py línea 512
domain = [
    ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
    ('move_id.state', '=', 'posted'),
    ('move_id.sales_channel_id.name', '!=', 'INTERNACIONAL'),  # ✅ Modificado
    ('product_id.categ_id', 'not in', [315, 333, 304, 314, 318, 339]),
    ('product_id.commercial_line_national_id.name', 'not ilike', 'VENTA INTERNACIONAL')
]
```

**Cambio reciente:** Filtro de canal cambió de `= 'NACIONAL'` a `!= 'INTERNACIONAL'` para coincidir con otro proyecto (incluye EXPORTACIÓN, ECOMMERCE, etc.)

---

## 📈 DATOS CLAVE

### **Supabase (Año 2025 Completo)**
- **Total Registros:** 31,982
- **Total Ventas:** S/ 55,788,910
- **Distribución Mensual:**
  - Enero: 1,047 registros | S/ 1,725,416
  - Febrero: 2,330 registros | S/ 4,659,449
  - Marzo: 2,833 registros | S/ 5,281,547
  - Abril: 2,350 registros | S/ 4,411,159
  - Mayo: 2,796 registros | S/ 5,572,417
  - Junio: 2,250 registros | S/ 3,352,799
  - Julio: 2,522 registros | S/ 3,583,024
  - Agosto: 3,048 registros | S/ 4,047,672
  - Septiembre: 3,451 registros | S/ 4,720,678
  - Octubre: 3,349 registros | S/ 4,201,472
  - Noviembre: 2,949 registros | S/ 6,021,356
  - Diciembre: 3,057 registros | S/ 8,211,919

### **Odoo (Datos en Tiempo Real 2026)**
- **Conexión:** amah.odoo.com
- **Base de Datos:** amah-main-9110254
- **Usuario:** jonathan.cerda@agrovetmarket.com

---

## 🎨 DISEÑO Y UX

### **Paleta de Colores**
- Principal: #1890ff (azul corporativo)
- Éxito: #52c41a (verde)
- Advertencia: #faad14 (amarillo/naranja)
- Error: #ff4d4f (rojo)
- Fondo: #f0f2f5

### **Tipografía**
- Primaria: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif
- Tamaños: 24px (títulos), 16px (texto), 12-14px (tablas)

### **Responsive**
- ✅ Desktop (1920x1080)
- ⚠️ Tablet (parcial)
- ❌ Mobile (no optimizado)

---

## 🚀 PRÓXIMAS PRIORIDADES SUGERIDAS

### **Prioridad ALTA** (Implementar primero)
1. **Heatmap de Actividad** - Código existe, solo falta renderizar
2. **Frecuencia de Compra** - KPI crítico según PRD
3. **Ticket Promedio Histórico** - Tendencia mensual
4. **Performance por Vendedor** - Top/Bottom rankings

### **Prioridad MEDIA**
5. **Mapa Geográfico** - Visualización por provincias
6. **Ventas por Canal** - Distribución porcentual
7. **Análisis Productos Completo** - Top 20 / Bottom 10

### **Prioridad BAJA** (Futuro)
8. **Tasa de Conversión** - Requiere datos adicionales
9. **Ciclo de Venta** - Análisis avanzado
10. **Sistema de Alertas** - Notificaciones automáticas

---

## 📝 NOTAS IMPORTANTES

1. **Memoria Render.com:** Supabase reduce uso de 27,000+ registros Odoo a ~2,000 por mes
2. **Filtro Internacional:** Cambio reciente incluye más canales (EXPORTACIÓN, ECOMMERCE)
3. **Caché:** Sistema de archivos .pkl acelera carga pero requiere limpieza manual
4. **Virtual Environment:** CRÍTICO usar `.venv` para acceso a módulo Supabase
5. **Sincronización:** Datos 2025 estáticos en Supabase, 2026+ dinámicos desde Odoo

---

## 🔗 ARCHIVOS CLAVE

- **Backend Principal:** `app.py` (2,055 líneas)
- **Gestor Odoo:** `odoo_manager.py` (1,059 líneas)
- **Gestor Supabase:** `supabase_manager.py`
- **Template Principal:** `templates/dashboard_clean.html` (1,923 líneas)
- **Estilos:** `static/css/style.css`
- **Scripts:** `static/js/script.js`
- **PRD Completo:** `PRD_dashboard_direccion.html` (769 líneas)
- **Documentación:** `PROJECT_CONTEXT.md`, `RENDER_DEPLOY.md`, `SUPABASE_SETUP.md`

---

**Última Actualización:** 13 de enero de 2026 - Re-migración completa 2025 con nuevo filtro de canal
