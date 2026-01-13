# Configuración de Supabase para Datos Históricos

## 1. Configuración Inicial

### Agregar las credenciales de Supabase al archivo `.env`:

```env
# Supabase Configuration
SUPABASE_URL=https://ppmbwujtfueilifisxhs.supabase.co
SUPABASE_KEY=tu_clave_anon_key_aqui
```

**Importante:** Necesitas obtener tu `SUPABASE_KEY` (anon/public key) desde:
- Panel de Supabase → Project Settings → API → Project API keys → `anon` `public`

## 2. Instalación de Dependencias

```bash
pip install supabase==2.10.0 postgrest==0.18.0 tqdm==4.67.0
```

O instalar todas las dependencias:

```bash
pip install -r requirements.txt
```

## 3. Estructura de la Base de Datos

La migración crea automáticamente las siguientes tablas en Supabase:

### `sales_lines`
Almacena todas las líneas de venta históricas con:
- Información de factura (ID, nombre, fecha)
- Cliente (ID, nombre)
- Producto (ID, nombre, código)
- Cantidades y precios
- Datos comerciales (línea comercial, vendedor, canal, ubicación)
- Índices optimizados para consultas rápidas

### `sales_monthly_summary`
Resúmenes mensuales agregados para optimizar consultas:
- Ventas totales por mes/línea/vendedor
- Ventas IPN
- Conteos de facturas, productos, clientes

### `sales_goals`
Metas de ventas históricas por mes y línea comercial

## 4. Migración de Datos del 2025

### Ejecutar el script de migración:

```bash
python migrate_to_supabase.py
```

Este script:
1. ✅ Migra todas las líneas de venta del 2025 desde Odoo
2. ✅ Genera resúmenes mensuales agregados
3. ✅ Migra las metas desde Google Sheets
4. ✅ Verifica que los datos se migraron correctamente

**Nota:** La migración puede tardar varios minutos dependiendo del volumen de datos.

## 5. Integración con la Aplicación

El sistema ahora consulta automáticamente:
- **Supabase**: Para datos históricos del 2025 (rápido, sin consumir API de Odoo)
- **Odoo**: Para datos del año actual (2026+)

### Ventajas:
- ⚡ Consultas más rápidas para datos históricos
- 💰 Reduce consumo de API de Odoo
- 📊 Datos históricos siempre disponibles
- 🔄 Datos actuales siguen sincronizados con Odoo

## 6. Verificación

Para verificar que los datos se migraron correctamente:

```python
from supabase_manager import SupabaseManager

sb = SupabaseManager()

# Verificar si el año 2025 está en Supabase
if sb.is_year_in_supabase(2025):
    print("✅ Datos del 2025 disponibles en Supabase")
    
# Obtener resumen de ventas de enero 2025
data = sb.get_sales_data('2025-01-01', '2025-01-31')
print(f"Líneas de venta en enero 2025: {len(data)}")
```

## 7. Políticas de Seguridad (Row Level Security)

Se recomienda configurar políticas RLS en Supabase:

```sql
-- Permitir lectura a usuarios autenticados
CREATE POLICY "Allow read access to authenticated users"
ON sales_lines
FOR SELECT
TO authenticated
USING (true);

-- Similar para las otras tablas
```

## 8. Respaldo de Datos

Supabase proporciona respaldos automáticos, pero también puedes:

```bash
# Exportar datos de una tabla
python -c "
from supabase_manager import SupabaseManager
import json

sb = SupabaseManager()
data = sb.get_sales_data('2025-01-01', '2025-12-31')

with open('backup_2025.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
"
```

## 9. Monitoreo

Desde el panel de Supabase puedes:
- Ver estadísticas de uso de la API
- Monitorear consultas lentas
- Revisar logs de errores
- Analizar patrones de uso

## 10. Actualización de Datos

Si necesitas actualizar datos del 2025:

```python
# Opción 1: Re-ejecutar migración completa (borra y vuelve a insertar)
# Opción 2: Actualizar registros específicos usando supabase_manager.py
```

## Soporte

Si encuentras problemas:
1. Verifica que `SUPABASE_KEY` esté correctamente configurada
2. Revisa los logs de la migración
3. Consulta los logs en el panel de Supabase
4. Verifica que las políticas RLS permitan acceso
