# Dashboard de Ventas Farmacéuticas - Contexto del Proyecto

## 📋 Información General

**Nombre**: Dashboard de Ventas Farmacéuticas  
**Cliente**: AMAH (Empresa Farmacéutica)  
**Base de Datos**: Odoo (amah.odoo.com - amah-main-9110254)  
**Framework**: Flask + Python  
**Versión Python**: 3.13  
**Fecha de Última Actualización**: Diciembre 2025

---

## 🎯 Objetivo del Proyecto

Sistema de visualización de KPIs comerciales en tiempo real para analizar el desempeño de ventas farmacéuticas, comparando contra metas establecidas y proporcionando insights sobre clientes, productos y líneas comerciales.

---

## 🏗️ Arquitectura del Sistema

### Backend
- **Framework**: Flask (Python)
- **Conexión Datos**: Odoo XML-RPC
- **Gestión Metas**: Google Sheets API
- **Sistema de Caché**: Pickle (archivos .pkl)
- **Autenticación**: Usuario/Contraseña con variables de entorno

### Frontend
- **Motor de Templates**: Jinja2
- **Librerías de Gráficos**:
  - Chart.js (gráficos de barras y líneas)
  - ECharts (gráfico de ciclo de vida)
  - SVG + CSS (gauge de cobertura)
- **UI Components**: Bootstrap Icons, Flatpickr (selector de fechas)

### Estructura de Archivos
```
dashboard-ventas/
├── app.py                      # Aplicación principal Flask
├── odoo_manager.py            # Gestión de conexión a Odoo
├── google_sheets_manager.py   # Gestión de Google Sheets
├── conectar_odoo.py           # Utilidad de conexión
├── limpiar_cache.py           # Script para gestionar caché
├── credentials.json           # Credenciales Google Sheets
├── requirements.txt           # Dependencias Python
├── BITACORA.md               # Registro de cambios
├── manual.html               # Manual de usuario
├── __pycache__/
│   └── dashboard_cache/      # Archivos de caché .pkl
├── static/
│   ├── css/
│   │   └── style.css         # Estilos personalizados
│   └── js/
│       └── script.js         # Scripts JavaScript
└── templates/
    ├── base.html             # Template base
    ├── dashboard_clean.html  # Dashboard principal
    ├── login.html            # Página de login
    ├── meta.html             # Gestión de metas
    └── sales.html            # Tabla de ventas detallada
```

---

## 📊 Modelos de Datos (Odoo)

### Principales Modelos Utilizados

1. **account.move** (Facturas/Pedidos)
   - `id`, `move_id`: ID del pedido/factura
   - `balance`: Monto de la venta
   - `invoice_date`: Fecha de factura
   - `partner_id`: Cliente
   - `invoice_user_id`: Vendedor

2. **res.partner** (Clientes)
   - `id`: ID del cliente
   - `name`: Nombre del cliente
   - `sales_channel_id`: Canal de ventas
   - `active`: Estado activo/inactivo

3. **product.product** (Productos)
   - `id`: ID del producto
   - `name`: Nombre del producto
   - `product_tmpl_id`: Template del producto

4. **sale.order** (Órdenes de Venta)
   - `id`: ID de la orden
   - `name`: Número de orden
   - `note_delivery`: Observaciones de entrega

5. **sale.order.line** (Líneas de Orden)
   - `order_id`: ID de la orden
   - `route_id`: Ruta de entrega (Fabricar por pedido: ID 18, 19)

### Campos Personalizados
- `commercial_line_national_id`: Línea comercial nacional
- `product_life_cycle`: Ciclo de vida del producto (nuevo/viejo)
- `sales_channel_id`: Canal de ventas

---

## 🔑 Funcionalidades Principales

### 1. Sistema de Caché Inteligente
**Ubicación**: `app.py` (líneas 37-80)

```python
def get_cached_data(year, month):
    """Obtiene datos desde caché si existen"""
    
def save_to_cache(year, month, data):
    """Guarda datos en caché para futuras consultas"""
    
def is_current_month(year, month):
    """Verifica si es el mes actual (no cachear)"""
```

**Comportamiento**:
- ✅ Meses pasados: Carga instantánea desde caché (.pkl)
- 🔄 Mes actual: Siempre consulta datos frescos desde Odoo
- 📁 Ubicación caché: `__pycache__/dashboard_cache/`
- 🔑 Formato nombre: `dashboard_{YYYY}_{MM}.pkl`

### 2. KPIs Principales

#### Meta vs Venta
- **Meta Total**: Obtenida desde Google Sheets
- **Venta Total**: Suma de `balance` de facturas
- **% Avance**: (Venta / Meta) × 100
- **Brecha Comercial**: Meta - Venta

#### Productos Nuevos (IPN)
- **Filtro**: `product_life_cycle == 'nuevo'`
- **Meta IPN**: 15% de meta total
- **Venta IPN**: Suma de ventas de productos nuevos

#### Cobertura de Clientes
**Ubicación**: `app.py` (líneas 590-660)

```python
cobertura_clientes = (clientes_activos / total_cartera) × 100
```

- **Clientes Activos**: Clientes con ventas en el período
- **Total Cartera**: Clientes activos en res.partner del año
- **Rangos de Objetivo**:
  - 🔴 < 50%: BAJO
  - 🟠 50-65%: REGULAR
  - 🟡 65-70%: META ALCANZADA
  - 🟢 ≥ 70%: EXCELENTE

#### Frecuencia de Compra
**Ubicación**: `app.py` (líneas 662-730)

```python
frecuencia = pedidos_únicos / clientes_activos
```

- **Agrupación**: Por Línea Comercial
- **Pedidos Únicos**: Count distinct de `move_id`
- **Clientes Activos**: Set de `partner_name` por línea
- **Rangos de Interpretación**:
  - 🔴 < 1: Riesgo (cliente ocasional)
  - 🟡 1-2: Estándar industria
  - 🟢 ≥ 2: Muy bueno (recurrencia saludable)

### 3. Visualizaciones

#### Gráfico de Cobertura (SVG Gauge)
**Ubicación**: `templates/dashboard_clean.html` (líneas 207-344)

- Gauge circular con gradientes
- Radio: 130px
- Circunferencia: 817px
- Animación con `stroke-dashoffset`
- Marcadores visuales en 50%, 65%, 70%

#### Gráfico de Frecuencia (Chart.js)
**Ubicación**: `templates/dashboard_clean.html` (líneas 347-437)

- Gráfico de barras horizontal
- Colores según umbral de frecuencia
- Tooltip con detalles (clientes, pedidos, frecuencia)
- Tabla complementaria con detalle por línea

#### Gráfico Ciclo de Vida (ECharts)
**Ubicación**: `templates/dashboard_clean.html` (líneas 986-1037)

- Gráfico de barras apiladas
- Series: Productos Nuevos vs Otros
- Agrupado por línea comercial

#### Gráfico de Ventas por Línea (Chart.js)
**Ubicación**: `templates/dashboard_clean.html` (líneas 1111-1198)

- Gráfico de líneas con puntos
- Comparación: Venta vs Meta vs IPN
- Eje Y formateado en miles

### 4. Normalización de Datos

#### Líneas Comerciales
**Ubicación**: `app.py` (líneas 122-138)

```python
def normalizar_linea_comercial(nombre_linea):
    """Agrupa GENVET y MARCA BLANCA como TERCEROS"""
    if 'GENVET' in nombre_linea or 'MARCA BLANCA' in nombre_linea:
        return 'TERCEROS'
    return nombre_linea
```

#### Filtros Aplicados
- ❌ Excluye: VENTA INTERNACIONAL
- ✅ Incluye solo ventas con `balance != 0`
- 🔄 Reasigna usuarios específicos a canal ECOMMERCE

### 5. Tablas de Análisis

#### Ventas por Línea Comercial
**Columnas**:
- Línea Comercial
- Venta PN (Productos Nuevos)
- % Meta
- Meta
- Venta Total
- % Avance
- % IPN
- Meta IPN
- Venta Ruta 18/19

#### Análisis de Clientes por Línea
**Columnas**:
- Línea Comercial
- Venta Total
- N° Clientes
- Ticket Promedio

#### Frecuencia de Compra por Línea
**Columnas**:
- Línea Comercial
- N° Clientes Activos
- Q Pedidos
- Frecuencia (Pedidos/Cliente)

---

## 🔐 Seguridad y Autenticación

### Variables de Entorno (.env)
```
ODOO_URL=https://amah.odoo.com
ODOO_DB=amah-main-9110254
ODOO_USERNAME=usuario@empresa.com
ODOO_PASSWORD=contraseña_segura
FLASK_SECRET_KEY=clave_secreta_flask
```

### Control de Acceso
- **Usuarios Normales**: Acceso solo a dashboard
- **Administradores**: Acceso a:
  - Dashboard
  - Tabla de ventas detallada (`/sales`)
  - Gestión de metas (`/meta`)

**Validación Admin**: `app.py` (líneas 222-245)
```python
is_admin = username in ['admin@amah.com', 'gerencia@amah.com']
```

---

## 📈 Métricas y Cálculos Clave

### Avance Lineal
```python
avance_lineal_pct = (dia_actual / dias_del_mes) × 100
```

### Ritmo Diario Requerido
```python
ritmo_diario = (meta_total - venta_total) / dias_laborables_restantes
```
**Días laborables**: Lunes a Sábado

### Vencimiento a 6 Meses
Productos con fecha de vencimiento <= 6 meses desde hoy

### Ticket Promedio
```python
ticket_promedio = venta_total / num_clientes
```

---

## 🎨 Diseño Visual

### Paleta de Colores
- **Principal**: `#875A7B` (Morado corporativo)
- **Éxito**: `#52c41a` (Verde)
- **Advertencia**: `#faad14` (Amarillo/Naranja)
- **Riesgo**: `#ff4d4f` (Rojo)
- **Info**: `#1890ff` (Azul)

### Estilos CSS
**Ubicación**: `static/css/style.css`

- Diseño responsive con Grid CSS
- Tarjetas con sombras y bordes redondeados
- Gradientes en gráficos
- Animaciones suaves (transitions)

---

## 🔄 Flujo de Datos

### 1. Login
```
Usuario/Password → Validación Odoo → Sesión Flask → Dashboard
```

### 2. Carga de Dashboard
```
Seleccionar Mes → Verificar Caché → 
  ├─ Si existe y no es mes actual → Cargar desde caché (instantáneo)
  └─ Si no existe o es mes actual → Consultar Odoo → Procesar datos → Guardar caché
```

### 3. Procesamiento de Datos
```
Odoo XML-RPC → 
  ├─ account.move (facturas)
  ├─ res.partner (clientes)
  ├─ product.product (productos)
  ├─ sale.order (pedidos)
  └─ sale.order.line (líneas de pedido)
→ Cruzar datos (JOIN manual) → 
→ Aplicar filtros y normalizaciones →
→ Calcular KPIs →
→ Agrupar por línea/canal/producto →
→ Renderizar template
```

---

## 🐛 Debugging y Logs

### Logs del Sistema
**Formato**:
```python
print(f"✅ Conexión exitosa")
print(f"📊 Datos obtenidos: {count} registros")
print(f"🔍 Filtrando...")
print(f"❌ Error: {mensaje}")
```

### Herramientas de Debug
- Flask Debug Mode: Activado en desarrollo
- Logs en terminal: Tiempo de consultas, cantidad de registros
- Console.log en navegador: Estado de gráficos

### Errores Comunes

1. **Error de Caché**
   - **Causa**: Datos antiguos sin nuevas variables
   - **Solución**: Limpiar caché con `limpiar_cache.py`

2. **Gráficos no se muestran**
   - **Causa**: Variables undefined en JavaScript
   - **Solución**: Agregar `|default([])` en templates

3. **Sesión expirada**
   - **Causa**: Timeout de conexión Odoo
   - **Solución**: Re-login

---

## 🚀 Deployment

### Requisitos de Sistema
- Python 3.13+
- Conexión a Internet (Odoo cloud)
- Acceso a Google Sheets API
- 512MB RAM mínimo
- 1GB espacio disco (para caché)

### Instalación
```bash
# 1. Clonar proyecto
cd dashboard-ventas

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar .env
cp .env.example .env
nano .env

# 4. Configurar credenciales Google Sheets
# Colocar credentials.json en la raíz

# 5. Ejecutar
python app.py
```

### Variables de Entorno Requeridas
- `ODOO_URL`
- `ODOO_DB`
- `ODOO_USERNAME`
- `ODOO_PASSWORD`
- `FLASK_SECRET_KEY`

---

## 📚 Dependencias Python

```txt
Flask==3.0.0
xmlrpc==1.0.1
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
gspread==5.12.0
python-dotenv==1.0.0
Werkzeug==3.0.1
```

---

## 🔮 Próximas Mejoras

### Funcionalidades Pendientes
- [ ] Exportar dashboard a PDF
- [ ] Alertas por email cuando se cumplen metas
- [ ] Comparativa año contra año
- [ ] Predicción de ventas con ML
- [ ] Dashboard móvil optimizado
- [ ] API REST para integraciones

### Optimizaciones Técnicas
- [ ] Migrar caché a Redis
- [ ] Implementar WebSockets para actualizaciones en tiempo real
- [ ] Compresión de datos en caché
- [ ] Lazy loading de gráficos
- [ ] PWA (Progressive Web App)

---

## 👥 Contactos y Soporte

**Desarrollador**: GitHub Copilot  
**Cliente**: AMAH  
**Documentación**: `BITACORA.md`, `manual.html`  
**Versión Actual**: 2.5.0 (Diciembre 2025)

---

## 📝 Notas Importantes

1. **Caché**: Los datos del mes actual NUNCA se cachean para garantizar información fresca
2. **Horario**: El dashboard considera días laborables de Lunes a Sábado
3. **Moneda**: Todos los valores están en la moneda base de Odoo (sin símbolo)
4. **Precisión**: Los cálculos de porcentaje usan 2 decimales
5. **Seguridad**: Las credenciales NUNCA deben commitearse al repositorio

---

*Última actualización: 17 de diciembre de 2025*
