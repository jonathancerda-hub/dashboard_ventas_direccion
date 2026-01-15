# 🚀 Dashboard de Ventas AMAH - Contexto del Proyecto

**VERSIÓN COMPLETA Y DETALLADA PARA ITERACIÓN DIARIA**

---

## ⚡ INICIO RÁPIDO (CRÍTICO - LEER PRIMERO)

### 🔴 ACTIVACIÓN ENTORNO VIRTUAL (OBLIGATORIO)

**CADA SESIÓN DEBE COMENZAR ACTIVANDO EL ENTORNO VIRTUAL:**

```powershell
cd "C:\Users\jcerda\Desktop\DashBoard Direccion"
& ".venv\Scripts\Activate.ps1"
```

**VERIFICAR ACTIVACIÓN:**
- El prompt debe mostrar `(.venv)` al inicio
- Si NO aparece `(.venv)`, NO ejecutar código Python

**PROBLEMA COMÚN:**
```
ModuleNotFoundError: No module named 'flask'
```
**SOLUCIÓN:** Activar .venv primero

---

### 🎯 COMANDOS ESENCIALES

```powershell
# 1. Activar entorno virtual
& ".venv\Scripts\Activate.ps1"

# 2. Ejecutar aplicación
python app.py

# 3. Acceder dashboard
# http://localhost:5000

# 4. Limpiar caché si hay problemas
python limpiar_cache.py

# 5. Inspeccionar caché actual
python inspeccionar_cache.py
```

---

## 📊 RESUMEN EJECUTIVO

### Información General

- **Cliente**: AMAH (Empresa Farmacéutica Veterinaria)
- **Propósito**: Dashboard analítico de ventas con segmentación RFM por canal
- **Framework**: Flask 3.0.0 + Python 3.13
- **Frontend**: Bootstrap 5 + Chart.js + ECharts + Leaflet.js
- **Fuentes de Datos**: Odoo 16 (XML-RPC) + Supabase PostgreSQL
- **Sistema de Caché**: Archivos pickle con TTL de 30 minutos
- **Fecha Última Actualización**: Enero 2026

### Funcionalidades Principales

1. **Análisis RFM (Recency, Frequency, Monetary)** con segmentación por canal
2. **Ventas por Producto y Categoría** con gráficos interactivos
3. **Mapa Geográfico** de ventas por región
4. **Análisis de Rentabilidad** por producto y categoría
5. **Filtros Dinámicos** por año, mes, canal de venta
6. **Sistema de Autenticación** con Google OAuth

---

## 🏗️ ARQUITECTURA DEL SISTEMA

### Arquitectura de Datos DUAL (CRÍTICO)

**EL SISTEMA USA DOS FUENTES DE DATOS SEGÚN EL AÑO:**

```
┌─────────────────────────────────────────────────────────────┐
│                    SELECCIÓN DE AÑO                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ≤ 2025                          ≥ 2026                     │
│     ↓                               ↓                        │
│  SUPABASE                         ODOO                       │
│  PostgreSQL                    XML-RPC API                   │
│  (Histórico)                   (Tiempo Real)                 │
│     ↓                               ↓                        │
│  31,982 registros           Consultas dinámicas              │
│  Campo: 'canal'             Campo: 'sales_channel_id'        │
│  Valores: ECOMMERCE,        Requiere: JOIN con res.partner   │
│           AGROVET,                                            │
│           PETMEDICA, etc.                                     │
└─────────────────────────────────────────────────────────────┘
```

### Campo 'Canal' - Diferencias Críticas

| Aspecto | Supabase (≤2025) | Odoo (≥2026) |
|---------|------------------|--------------|
| **Nombre Campo** | `canal` | `sales_channel_id` |
| **Tipo de Dato** | String directo | Relacional (ID) |
| **Valores** | Nombres de equipo: ECOMMERCE, AGROVET, PETMEDICA | IDs que requieren JOIN |
| **Tabla** | `sale_order_line` | `res.partner` |
| **Procesamiento** | Clasificación directa en código | Query adicional a res.partner |

### Clasificación de Canales (Grupos de Venta)

**Según Grupos de Venta en Odoo:**

```python
DIGITAL (Canales Digitales):
  - ECOMMERCE (código 108)
  - AIRBNB (código 110)
  - EMPLEADOS (código 109)

NACIONAL (Distribución Tradicional):
  - DISTRIBUIDORES (código 101)
  - MAYORISTAS (código 102)
  - GRANJAS (código 103)
  - USUARIO FINAL (código 104)
  - INSTITUCIONES (código 105)
  - MINORISTAS (código 106)
  - MINO
  - Cualquier otro grupo no listado en DIGITAL
```

---

## 🔧 CONFIGURACIÓN DEL ENTORNO

### Virtual Environment (.venv)

**UBICACIÓN:**
```
C:\Users\jcerda\Desktop\DashBoard Direccion\.venv\
```

**ACTIVACIÓN (PowerShell):**
```powershell
& ".venv\Scripts\Activate.ps1"
```

**VERIFICACIÓN:**
```powershell
python --version  # Debe mostrar: Python 3.13.x
pip list          # Debe mostrar Flask, requests, etc.
```

### Dependencias Principales (requirements.txt)

```
Flask==3.0.0
gunicorn==21.2.0
requests==2.31.0
python-dotenv==1.0.0
google-auth==2.25.2
google-auth-oauthlib==1.2.0
supabase==2.1.0
```

### Variables de Entorno

**ARCHIVO:** No hay `.env` (credenciales en código por simplicidad interna)

**CREDENCIALES HARDCODED EN:**
- `odoo_manager.py`: URL, DB, usuario, contraseña Odoo
- `app.py`: Supabase URL y Key
- `google_sheets_manager.py`: Client ID y Secret de Google OAuth

---

## 📁 ESTRUCTURA DE ARCHIVOS

### Archivos Principales

```
dashboard-ventas/
│
├── app.py (2,490 líneas)              # Aplicación Flask principal
│   ├── Líneas 774-840: Cálculo RFM base
│   ├── Líneas 863-875: Captura canal Supabase + clasificación
│   ├── Líneas 905-935: Query canal Odoo desde res.partner
│   └── Líneas 945-1010: Scoring RFM diferenciado por canal
│
├── odoo_manager.py                    # Conexión XML-RPC a Odoo
├── google_sheets_manager.py           # Autenticación Google OAuth
├── limpiar_cache.py                   # Limpieza manual de caché
├── inspeccionar_cache.py              # Inspección de archivos caché
├── generate_cache.py                  # Pre-generación de caché
│
├── templates/
│   ├── dashboard_clean.html (2,324)   # UI principal del dashboard
│   │   ├── Líneas 545-570: Filtro dropdown canal
│   │   ├── Líneas 1638-1645: Datos globales rfmPorCanal
│   │   └── Líneas 1833-1933: Función filtrarRFMPorCanal()
│   ├── base.html                      # Template base
│   ├── login.html                     # Página de login
│   └── sales.html                     # Vista de ventas
│
├── static/
│   ├── css/style.css                  # Estilos personalizados
│   └── js/script.js                   # JavaScript dashboard
│
├── __pycache__/
│   └── dashboard_cache/               # Archivos pickle de caché
│       ├── dashboard_data_2025_01.pkl
│       ├── dashboard_data_2026_01.pkl
│       └── ...
│
├── requirements.txt                   # Dependencias Python
├── render.yaml                        # Configuración Render.com
├── .gitignore                         # Archivos ignorados por Git
└── PROJECT_CONTEXT.md                 # ESTE ARCHIVO (ignorado en Git)
```

### Archivos de Soporte/Scripts

```
fix_*.py                               # Scripts de corrección sintaxis
consultar_canales.py                   # Script consulta canales Odoo
verificar_canal_supabase.py            # Verificación campo canal Supabase
restore_file.py                        # Restauración de archivos
update_map.py                          # Actualización mapa geográfico
```

---

## 🗄️ FUENTES DE DATOS

### 1. Supabase PostgreSQL (Datos Históricos ≤2025)

**TABLA PRINCIPAL:** `sale_order_line`

**CAMPOS CLAVE:**
```sql
- date_order          # Fecha de la orden
- partner_name        # Nombre del cliente
- product_name        # Nombre del producto
- category_name       # Categoría del producto
- price_unit          # Precio unitario
- product_uom_qty     # Cantidad
- price_subtotal      # Subtotal sin impuestos
- state               # Estado: 'sale' o 'done'
- canal               # ⚠️ CAMPO CRÍTICO: Contiene nombre del equipo directamente
```

**ESTADÍSTICAS:**
- Total registros: 31,982
- Líneas promedio/mes: ~960
- Valores campo 'canal':
  - ECOMMERCE: 134 líneas/mes
  - AGROVET: 444 líneas/mes
  - PETMEDICA: 306 líneas/mes
  - AVIVET: 41 líneas/mes
  - PETNUTRISCIENCE: 41 líneas/mes
  - OFICINA: 34 líneas/mes
  - MARCA BLANCA: variable

**CONEXIÓN:**
```python
from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
```

### 2. Odoo 16 XML-RPC (Datos Tiempo Real ≥2026)

**SERVIDOR:** amah.odoo.com  
**BASE DE DATOS:** amah-main-9110254  
**PROTOCOLO:** XML-RPC sobre HTTPS

**MODELOS PRINCIPALES:**

#### sale.order.line (Líneas de venta)
```python
fields = [
    'order_id',         # Relación a sale.order
    'product_id',       # Relación a product.product
    'product_uom_qty',  # Cantidad
    'price_unit',       # Precio unitario
    'price_subtotal',   # Subtotal
]
```

#### res.partner (Clientes)
```python
fields = [
    'id',               # ID del cliente
    'name',             # Nombre del cliente
    'sales_channel_id', # ⚠️ CAMPO CRÍTICO: ID del canal (relacional)
    'city',             # Ciudad
    'state_id',         # Estado/Región
]
```

**QUERY CANAL EN ODOO:**
```python
# app.py líneas 905-935
partners = models.execute_kw(
    db, uid, password,
    'res.partner', 'search_read',
    [[['id', 'in', partner_ids]]],
    {'fields': ['id', 'name', 'sales_channel_id']}
)

for partner in partners:
    if partner.get('sales_channel_id'):
        canal_id, canal_nombre = partner['sales_channel_id']
        # Clasificar según nombre del canal
```

**GRUPOS DE VENTA (Odoo):**
- **DIGITAL (3 grupos):**
  - ECOMMERCE (108)
  - AIRBNB (110)
  - EMPLEADOS (109)

- **NACIONAL (7+ grupos principales):**
  - DISTRIBUIDORES (101)
  - MAYORISTAS (102)
  - GRANJAS (103)
  - USUARIO FINAL (104)
  - INSTITUCIONES (105)
  - MINORISTAS (106)
  - MINO
  - Otros grupos no digitales

---

## 🎨 FUNCIONALIDADES PRINCIPALES

### 1. Análisis RFM por Canal

**IMPLEMENTACIÓN:** `app.py` líneas 774-1050

**LÓGICA:**

```python
# PASO 1: Calcular métricas por cliente
for venta in ventas:
    cliente = venta['partner_name']
    fecha = venta['date_order']
    monto = venta['price_subtotal']
    
    # Recency: días desde última compra
    canal_upper = canal_directo.upper()
    # DIGITAL: ECOMMERCE, AIRBNB, EMPLEADOS
    if 'ECOMMERCE' in canal_upper or 'AIRBNB' in canal_upper or 'EMPLEADO' in canal_upper:
        cliente_canal[cliente] = 'DIGITAL'
    # NACIONAL: Todo lo demás (DISTRIBUIDORES, MAYORISTAS, GRANJAS, etc.)
    else:
        cliente_canal[cliente] = 'NACIONAL'
else:
    # ODOO: Query a res.partner.sales_channel_id
    partners = models.execute_kw(...)
    canal_nombre = partner['sales_channel_id'][1].upper()
    if 'ECOMMERCE' in canal_nombre or 'AIRBNB' in canal_nombre or 'EMPLEADO' in canal_nombre:
        canal = 'DIGITAL'
    else:
        canal = 'NACIONAL'EDICA', ...]:
        cliente_canal[cliente] = 'NACIONAL'
    else:
        cliente_canal[cliente] = 'OTROS'
else:
    # ODOO: Query a res.partner.sales_channel_id
    partners = models.execute_kw(...)
    # Clasificar según sales_channel_id[1] (nombre)

# PASO 3: Scoring diferenciado por canal
canal = cliente_canal.get(cliente, 'OTROS')

if canal == 'DIGITAL':
    # Clientes digitales compran frecuentemente
    if recency <= 20: r_score = 5
    elif recency <= 45: r_score = 4
    # ...
    if frequency >= 4: f_score = 5
    elif frequency >= 2: f_score = 4
    # ...
    
elif canal == 'NACIONAL':
    # Distribuidores compran menos frecuente pero mayor volumen
    if recency <= 60: r_score = 5
    elif recency <= 120: r_score = 4
    # ...
    if frequency >= 2: f_score = 5
    elif frequency >= 1: f_score = 4
    # ...
```

**UMBRALES RFM:**

| Métrica | DIGITAL | NACIONAL | OTROS |
|---------|---------|----------|-------|
| **Recency (días)** | | | |
| Score 5 | ≤20 | ≤60 | ≤30 |
| Score 4 | ≤45 | ≤120 | ≤90 |
| Score 3 | ≤90 | ≤180 | ≤180 |
| Score 2 | ≤180 | ≤270 | ≤365 |
| Score 1 | >180 | >270 | >365 |
| **Frequency (órdenes)** | | | |
| Score 5 | ≥4 | ≥2 | ≥3 |
| Score 4 | ≥2 | ≥1 | ≥2 |
| Score 3 | =1 | =1 | =1 |
| Score 2 | <1 | <1 | <1 |
| Score 1 | 0 | 0 | 0 |
| **Monetary (percentil)** | | | |
| Score 5 | ≥80% | ≥80% | ≥80% |
| Score 4 | ≥60% | ≥60% | ≥60% |
| Score 3 | ≥40% | ≥40% | ≥40% |
| Score 2 | ≥20% | ≥20% | ≥20% |
| Score 1 | <20% | <20% | <20% |

**SEGMENTOS RFM:**

```python
# Basado en suma de scores (R + F + M)
segmentos = {
    'Champions': total_score >= 13,        # 555, 554, 545, 544
    'Loyal Customers': 10 <= score < 13,   # 445, 444, 543
    'Potential Loyalist': 8 <= score < 10, # 435, 434, 443
    'At Risk': 5 <= score < 8,             # 344, 343, 334
    'Lost': score < 5                      # Cualquier combinación baja
}
```

### 2. Filtro de Canal en UI

**IMPLEMENTACIÓN:** `dashboard_clean.html` líneas 545-570

```html
<div class="col-md-3">
    <label for="canalFilter">Canal de Venta:</label>
    <select id="canalFilter" class="form-select" onchange="filtrarRFMPorCanal()">
        <option value="TODOS">📊 Todos los Canales</option>
        <option value="DIGITAL">💻 Digital (ECOMMERCE)</option>
        <option value="NACIONAL">🏢 Nacional (Distribuidores)</option>
        <option value="OTROS">📦 Otros Canales</option>
    </select>
</div>
```

**FUNCIÓN JAVASCRIPT:** `dashboard_clean.html` líneas 1833-1933

```javascript
function filtrarRFMPorCanal() {
    const canalSeleccionado = document.getElementById('canalFilter').value;
    
    let datosFiltrados;
    if (canalSeleccionado === 'TODOS') {
        datosFiltrados = rfmPorCanal.total;
    } else {
        datosFiltrados = rfmPorCanal[canalSeleccionado];
    }
    
    // Actualizar gráfico RFM
    actualizarGraficoRFM(datosFiltrados);
    
    // Actualizar tabla de clientes
    actualizarTablaRFM(canalSeleccionado);
}
```

### 3. Sistema de Caché

**UBICACIÓN:** `__pycache__/dashboard_cache/`

**ESTRUCTURA ARCHIVO:**
```
dashboard_data_{año}_{mes}.pkl
```

**LÓGICA TTL:**
```python
# Mes actual: TTL 30 minutos
if (año == año_actual) and (mes == mes_actual):
    cache_age_minutes = (now - cache_modified_time).total_seconds() / 60
    if cache_age_minutes > 30:
        regenerar_cache()

# Meses pasados: Sin expiración (datos históricos)
else:
    usar_cache_indefinidamente()
```

**CONTENIDO CACHE:**
```python
cache_data = {
    'ventas_por_mes': {...},
    'ventas_por_producto': {...},
    'ventas_por_categoria': {...},
    'rfm_data': {...},
    'rfm_por_canal': {
        'total': {...},
        'DIGITAL': {...},
        'NACIONAL': {...},
        'OTROS': {...}
    },
    'clientes_rfm': [...],
    'mapa_data': {...},
    # ... más datos
}
```

### 4. Autenticación Google OAuth

**IMPLEMENTACIÓN:** `google_sheets_manager.py`

**FLUJO:**
1. Usuario accede a `/` → Redirige a `/login`
2. Click en "Iniciar sesión con Google"
3. Callback a `/oauth2callback`
4. Verificación de email en `allowed_users.json`
5. Sesión Flask con `session['user']`

**USUARIOS PERMITIDOS:** `allowed_users.json`
```json
{
    "allowed_emails": [
        "usuario1@amah.com",
        "usuario2@amah.com"
    ]
}
```

---

## 🔄 CAMBIOS RECIENTES (Enero 2026)

### 1. Implementación RFM por Canal ✅

**FECHA:** Enero 2026  
**PROBLEMA INICIAL:** RFM usaba mismos umbrales para todos los clientes, marcando distribuidores (compras mensuales grandes) como "Lost" incorrectamente.

**SOLUCIÓN:**
- Diferenciación de umbrales por tipo de cliente (DIGITAL vs NACIONAL)
- Captura campo 'canal' desde ambas fuentes de datos
- Clasificación automática: ECOMMERCE→DIGITAL, marcas principales→NACIONAL
- UI con filtro dropdown de 4 opciones
- JavaScript para filtrado en tiempo real sin reload

**ARCHIVOS MODIFICADOS:**
- `app.py` líneas 863-875 (captura canal Supabase)
- `app.py` líneas 905-935 (query canal Odoo)
- `app.py` líneas 945-1010 (scoring diferenciado)
- `dashboard_clean.html` líneas 545-570 (UI filtro)
- `dashboard_clean.html` líneas 1833-1933 (función JS filtrarRFMPorCanal)

### 2. Corrección Campo Canal 2025 ✅

**PROBLEMA:** Al seleccionar año 2025, columna "Canal" mostraba "N/A" para todos los clientes.

**CAUSA RAÍZ:** Campo 'canal' en Supabase contiene nombres de equipos (ECOMMERCE, AGROVET) no categorías (DIGITAL, NACIONAL).

**SOLUCIÓN:**
# DIGITAL: ECOMMERCE, AIRBNB, EMPLEADOS
if 'ECOMMERCE' in canal_upper or 'AIRBNB' in canal_upper or 'EMPLEADO' in canal_upper:
    cliente_canal[partner_name] = 'DIGITAL'
# NACIONAL: Todo lo demás (DISTRIBUIDORES, MAYORISTAS, GRANJAS, USUARIO FINAL, INSTITUCIONES, MINORISTAS, MINO, etc.)
else:
    cliente_canal[partner_name] = 'NACIONALAL'
elif canal_upper in ['AGROVET', 'PETMEDICA', 'INTERPET', 'AVIVET', 
                      'PETNUTRISCIENCE', 'MARCA BLANCA']:
    cliente_canal[partner_name] = 'NACIONAL'
else:
    cliente_canal[partner_name] = 'OTROS'
```

### 3. PROJECT_CONTEXT.md en .gitignore ✅

**RAZÓN:** Archivo contiene información sensible y contexto de desarrollo interno.

**MODIFICACIÓN .gitignore:**
```
# Project context (internal development)
PROJECT_CONTEXT.md
PROJECT_CONTEXT_backup_*.md
```

---

## 🐛 TROUBLESHOOTING

### Problema 1: ModuleNotFoundError

**ERROR:**
```
ModuleNotFoundError: No module named 'flask'
ModuleNotFoundError: No module named 'requests'
```

**CAUSA:** Entorno virtual no activado.

**SOLUCIÓN:**
```powershell
& ".venv\Scripts\Activate.ps1"
python app.py
```

**VERIFICACIÓN:**
```powershell
# Debe mostrar (.venv) en el prompt
(.venv) PS C:\Users\jcerda\Desktop\DashBoard Direccion>
```

### Problema 2: Canal muestra "N/A" en 2025

**CAUSA:** Campo 'canal' en Supabase contiene nombres de equipos, no categorías.

**VERIFICACIÓN:**
```powershell
python verificar_canal_supabase.py
# Debe mostrar: ECOMMERCE, AGROVET, PETMEDICA, etc.
```

**SOLUCIÓN:** Ya implementada en `app.py` líneas 863-875 (clasificación automática).

### Problema 3: Datos desactualizados

**CAUSA:** Caché del mes actual tiene más de 30 minutos.

**SOLUCIÓN:**
```powershell
python limpiar_cache.py
# O reiniciar la aplicación (regenera automáticamente)
```

**INSPECCIÓN:**
```powershell
python inspeccionar_cache.py
# Muestra edad de cada archivo caché
```

### Problema 4: Error de conexión Odoo

**ERROR:**
```
ConnectionError: Unable to connect to Odoo server
```

**CAUSAS POSIBLES:**
1. Sin conexión a internet
2. Servidor Odoo caído
3. Credenciales incorrectas en `odoo_manager.py`

**VERIFICACIÓN:**
```python
# En Python REPL con .venv activado
from odoo_manager import OdooManager
odoo = OdooManager()
odoo.uid  # Debe mostrar ID de usuario, no False
```

### Problema 5: RFM todos los clientes en "Lost"

**CAUSA:** Umbrales muy estrictos para el tipo de cliente.

**VERIFICACIÓN:** Revisar umbrales diferenciados en tabla de la sección "Funcionalidades Principales > 1. Análisis RFM por Canal".

**AJUSTE:** Modificar umbrales en `app.py` líneas 945-1010 según comportamiento real de cada canal.

### Problema 6: Mapa geográfico no carga

**CAUSA:** Leaflet.js no cargado o coordenadas inválidas.

**VERIFICACIÓN:**
```javascript
// En consola del navegador
typeof L  // Debe mostrar "object" no "undefined"
```

**SOLUCIÓN:** Verificar CDN de Leaflet en `dashboard_clean.html` header.

---

## 📈 ROADMAP Y MEJORAS FUTURAS

### Corto Plazo (1-2 semanas)

- [ ] Testing completo con datos 2025 y 2026 en producción
- [ ] Validar que todos los clientes muestran canal correcto (no "N/A")
- [ ] Optimizar queries Odoo (actualmente 2 queries: sale.order.line + res.partner)
- [ ] Añadir loading spinner en cambio de filtro canal

### Mediano Plazo (1 mes)

- [ ] Implementar caché Redis en lugar de archivos pickle
- [ ] Añadir filtro adicional por producto/categoría en RFM
- [ ] Dashboard de comparación año vs año
- [ ] Export Excel de tabla RFM filtrada por canal

### Largo Plazo (3+ meses)

- [ ] API REST para integración con otros sistemas
- [ ] Notificaciones automáticas de clientes "At Risk"
- [ ] Machine Learning para predicción de churn
- [ ] Dashboard mobile responsive completo

---

## 📝 NOTAS IMPORTANTES

### Datos Sensibles

**ARCHIVOS CON CREDENCIALES:**
- `odoo_manager.py`: URL, DB, usuario, password Odoo
- `app.py`: Supabase URL y Key
- `google_sheets_manager.py`: Client ID y Secret OAuth
- `allowed_users.json`: Lista de emails autorizados

**NO COMPARTIR ESTOS ARCHIVOS PÚBLICAMENTE**

### Performance

**TIEMPOS DE CARGA TÍPICOS:**
- Primera carga (sin caché): 15-30 segundos
- Cargas subsecuentes (con caché): 1-3 segundos
- Cambio de filtro canal (JavaScript): <1 segundo

**OPTIMIZACIONES:**
- Caché pickle reduce carga en 90%
- Queries Odoo ejecutan solo para mes actual
- Supabase devuelve datos pre-agregados

### Mantenimiento

**TAREAS SEMANALES:**
- Verificar logs de errores en consola
- Revisar tamaño de carpeta `dashboard_cache/` (limpiar si >100MB)
- Validar autenticación Google OAuth funcionando

**TAREAS MENSUALES:**
- Actualizar `allowed_users.json` si hay cambios de personal
- Revisar umbrales RFM vs comportamiento real de clientes
- Backup de caché del mes anterior

---

## 🆘 CONTACTO Y SOPORTE

**DESARROLLADOR:** GitHub Copilot (Claude Sonnet 4.5)  
**FECHA DOCUMENTACIÓN:** Enero 2026  
**VERSIÓN:** 2.0 - Completa y Detallada para Iteración Diaria

---

**FIN DEL DOCUMENTO**

---

*Este documento está diseñado para ser leído al inicio de cada sesión de desarrollo, garantizando contexto completo sobre arquitectura dual de datos, manejo diferenciado del campo 'canal', y requisitos críticos como activación del entorno virtual.*
