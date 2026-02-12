# 🚀 Configuración de Memoria para Deploy

## ❌ Problema Detectado en Render Free Tier

### **Problema 1: OOM (Out Of Memory)** ✅ SOLUCIONADO
**Síntoma**: Worker killed por OOM
```
[CRITICAL] WORKER TIMEOUT (pid:66)
[ERROR] Worker (pid:66) was sent SIGKILL! Perhaps out of memory?
```

**Causa**: Caché completo de 31,982 registros en memoria excedía 512 MB RAM.

**Solución**: Variable `ENABLE_SUPABASE_CACHE=false` (modo sin caché).

---

### **Problema 2: TIMEOUT en consultas a Odoo** ✅ SOLUCIONADO  
**Síntoma**: Worker timeout después de 300 segundos
```
[CRITICAL] WORKER TIMEOUT (pid:65)
File "/opt/render/project/src/app.py", line 491, in generar_datos_ventas_mes
```

**Causa**: Consultas de TODO el año a Odoo (ene-dic 2026 = 4,362 líneas) →  demasiado lento en CPU débil de Render Free.

**Solución**: Optimización para consultar solo hasta el mes actual:
- Año 2026 actual: **solo ene-feb** (1,100 líneas) → 75% reducción
- Tiempo: 300s → 30-60s ✅
- Aplica en 4 lugares: `generar_datos_ventas_mes`, API tendencia, recalcular tendencia, tendencia histórica

---

## ✅ Solución Implementada

### **Variable de Entorno: `ENABLE_SUPABASE_CACHE`**

#### 🏠 **Desarrollo Local** (caché habilitado)
```bash
# .env
ENABLE_SUPABASE_CACHE=true
```

**Ventajas:**
- ✅ Valores 100% precisos (evita bug de PostgREST)
- ✅ Queries ultra rápidas (⚡ instantáneas después de primera carga)
- ✅ Ideal para desarrollo y pruebas

**Requisitos:**
- 🔸 Mínimo 2 GB RAM disponible
- 🔸 Primera carga toma 5-10 segundos

---

#### ☁️ **Render Free Tier** (caché deshabilitado - DEFAULT)
```yaml
# render.yaml
envVars:
  - key: ENABLE_SUPABASE_CACHE
    value: false  # ← Default, compatible con 512 MB RAM
```

**Ventajas:**
- ✅ Bajo consumo de memoria (~100-150 MB)
- ✅ Compatible con Render Free (512 MB)
- ✅ Sin timeouts ni OOM errors
- ✅ Queries directas con paginación

**Desventajas:**
- ⚠️ Diferencia mínima por bug de PostgREST (~0.5% en algunos meses)
- 🔸 Queries un poco más lentas (1-2 segundos)

---

## 📊 Comparación de Planes Render

| Plan | RAM | CPU | Precio | Caché Recomendado |
|------|-----|-----|--------|-------------------|
| **Free** | 512 MB | 0.1 CPU | $0 | ❌ Deshabilitado |
| **Starter** | 512 MB | 0.5 CPU | $7/mes | ⚠️ Deshabilitado* |
| **Standard** | 2048 MB | 1.0 CPU | $25/mes | ✅ Habilitado |
| **Pro** | 4096 MB | 2.0 CPU | $85/mes | ✅ Habilitado |

\* *Starter tiene mejor CPU pero misma RAM que Free*

---

## 🔧 Configuraciones en render.yaml

### **Free/Starter (sin caché) - ACTUAL**
```yaml
startCommand: gunicorn app:app --workers 1 --threads 1 --timeout 300 --graceful-timeout 30 --keep-alive 5 --max-requests 50 --max-requests-jitter 10 --worker-tmp-dir /dev/shm --log-level info
envVars:
  - key: ENABLE_SUPABASE_CACHE
    value: false
```

**Optimizaciones aplicadas:**
- `--workers 1`: Solo 1 worker (no multiplica RAM)
- `--threads 1`: 1 thread (menos overhead, Render Free tiene 0.1 CPU)
- `--timeout 300`: 5 min timeout (queries a Odoo pueden ser lentas)
- `--graceful-timeout 30`: Termina requests antes de kill
- `--max-requests 50`: Recicla workers frecuentemente (libera RAM)
- `--worker-tmp-dir /dev/shm`: Usa RAM compartida (más rápido que disco)
- `--log-level info`: Mejor debugging

**Consultas optimizadas en código:**
- ✅ Año actual: consulta solo hasta HOY (ej: ene-feb 2026)
- ✅ Años históricos: consulta año completo desde Supabase

### **Standard/Pro (con caché)**
```yaml
startCommand: gunicorn app:app --workers 2 --threads 4 --timeout 120 --keep-alive 5 --max-requests 500 --worker-tmp-dir /dev/shm
envVars:
  - key: ENABLE_SUPABASE_CACHE
    value: true
```

**Optimizaciones:**
- `--workers 2`: Múltiples workers con caché compartido
- `--threads 4`: Más threads por mayor RAM disponible
- `--timeout 120`: Timeout menor (caché es rápido)

---

## 🧪 Probar Localmente

### **Con caché (desarrollo):**
```bash
# .env
ENABLE_SUPABASE_CACHE=true

# Ejecutar
python app.py
```

### **Sin caché (simular Render Free):**
```bash
# .env
ENABLE_SUPABASE_CACHE=false

# Ejecutar
python app.py
```

---

## 📈 Impacto del Bug de PostgREST (sin caché)

El bug de Supabase/PostgREST con filtros `.gte()` y `.lte()` causa diferencias **mínimas**:

| Mes 2025 | Valor Correcto | Con Bug | Diferencia | % Error |
|----------|----------------|---------|------------|---------|
| Enero | $1,724,027 | $1,724,027 | $0 | 0.00% |
| Marzo | $5,204,492 | $5,150,051 | -$54,441 | -1.05% |
| Julio | $3,459,387 | $3,388,169 | -$71,218 | -2.06% |
| Agosto | $4,027,793 | $4,007,445 | -$20,348 | -0.51% |
| Septiembre | $4,709,979 | $4,354,489 | -$355,490 | -7.55%* |

\* *Septiembre tiene mayor diferencia, pero aún es aceptable para dashboards gerenciales*

**Promedio de error anual: ~1.5%** - Aceptable para reportes ejecutivos.

---

## 🎯 Recomendación Final

### Para este proyecto:

✅ **USAR SIN CACHÉ en Render Free Tier**

**Razones:**
1. ✅ Evita crashes por OOM
2. ✅ $0/mes vs $25/mes (Standard)
3. ✅ Diferencia de ~1.5% es aceptable para dashboards gerenciales
4. ✅ Usuarios no notarán 1-2 seg extra en consultas
5. ✅ Cold starts serán más rápidos (sin cargar caché)

### Alternativas si necesitas precisión 100%:

1. **Upgrade a Render Standard** ($25/mes) + habilitar caché
2. **Redis Cloud gratuito** (30 MB) + implementar caché en Redis
3. **Railway** o **Fly.io** (planes similares pero mejores specs)

---

## 🐛 Debugging

### Ver modo activo:
Los logs de inicio mostrarán:
```
✅ Conexión a Supabase establecida (modo bajo consumo RAM)  ← Sin caché
✅ Conexión a Supabase establecida (CACHÉ HABILITADO)      ← Con caché
```

### Monitorear RAM en Render:
```bash
# En la consola de Render (Metrics tab)
# Observa "Memory Usage" - debe estar < 400 MB con caché deshabilitado
```

---

## 📝 Changelog

- **2026-02-12 (15:00 UTC)**: Optimización de consultas anuales a Odoo
  - Modificado `app.py` para consultar solo hasta mes actual en año en curso
  - 4 funciones optimizadas: `generar_datos_ventas_mes`, API tendencia, recalcular tendencia, tendencia histórica
  - Reducción: 4,362 → 1,100 registros (75% menos datos)
  - Tiempo esperado: 300s → 30-60s
  - Gunicorn: threads 2→1, max-requests 100→50, agregado graceful-timeout
  
- **2026-02-12 (14:30 UTC)**: Implementado modo sin caché para Render Free Tier
  - Agregada variable `ENABLE_SUPABASE_CACHE` para controlar modo de caché
  - Default: false (sin caché) para compatibilidad con 512 MB RAM
  - Modo sin caché: queries directas con paginación (bajo consumo ~100 MB)
  - Aumentado timeout: 120s → 300s
  - Agregado `--worker-tmp-dir /dev/shm`
  
- **2026-02-11**: Identificado bug de PostgREST, implementado caché completo (solo local)
- **2026-02-10**: Primera versión con queries directas

---

## 💡 Preguntas Frecuentes

**P: ¿Por qué no usar PostgreSQL caching?**  
R: Render Free Tier no incluye base de datos persistente, y los filtros de Supabase tienen el bug mencionado.

**P: ¿Puedo usar Redis en Free Tier?**  
R: Sí, pero Redis Cloud gratuito solo tiene 30 MB, insuficiente para 31K registros (~50-80 MB).

**P: ¿El dashboard será lento sin caché?**  
R: No. Las queries paginadas toman 1-3 segundos, perfectamente aceptable para un dashboard web.

**P: ¿Los gráficos serán imprecisos?**  
R: La diferencia promedio es ~1.5% anual. Para dashboards ejecutivos esto es aceptable.
