# 🚀 Guía de Despliegue en Render.com

## 📋 Pasos para Desplegar

### 1. Preparar el Repositorio

Asegúrate de que todos los cambios estén en GitHub:

```bash
git add .
git commit -m "Preparar para despliegue en Render"
git push origin main
```

### 2. Crear Cuenta en Render.com

1. Ve a https://render.com
2. Regístrate con tu cuenta de GitHub
3. Autoriza a Render para acceder a tus repositorios

### 3. Crear un Nuevo Web Service

1. Click en **"New +"** → **"Web Service"**
2. Selecciona el repositorio: `dashboard-ventas`
3. Configuración:
   - **Name:** `dashboard-ventas` (o el nombre que prefieras)
   - **Region:** Oregon (US West)
   - **Branch:** `main`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free (o el que prefieras)

### 4. Configurar Variables de Entorno

En la sección **Environment** de Render, agrega todas las variables del archivo `.env`:

#### Variables Requeridas:

```
SECRET_KEY=tu_clave_secreta_aqui
ADMIN_USERS=usuario1@ejemplo.com,usuario2@ejemplo.com
ODOO_URL=https://tu-odoo.com
ODOO_DB=nombre_base_datos
ODOO_USERNAME=tu_usuario_odoo
ODOO_PASSWORD=tu_password_odoo
```

#### Variables para Google Sheets:

**Opción 1: Usar archivo credentials.json**

1. Copia el contenido completo de `credentials.json`
2. En Render, crea variable `GOOGLE_CREDENTIALS_JSON`
3. Pega el JSON completo como valor
4. Modifica `google_sheets_manager.py` para leer desde variable de entorno

**Opción 2: Usar Google Service Account (Recomendado)**

```
GOOGLE_SERVICE_ACCOUNT_EMAIL=tu-service-account@proyecto.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n
GOOGLE_SHEET_NAME=MetasDashboardVentas
```

### 5. Modificaciones de Código Necesarias

#### A. Actualizar `google_sheets_manager.py`:

```python
import os
import json

# En el método __init__:
if os.getenv('GOOGLE_CREDENTIALS_JSON'):
    # Render: usar variable de entorno
    creds_dict = json.loads(os.getenv('GOOGLE_CREDENTIALS_JSON'))
    self.gc = gspread.service_account_from_dict(creds_dict)
else:
    # Local: usar archivo credentials.json
    self.gc = gspread.service_account(filename='credentials.json')
```

#### B. Actualizar `app.py` (puerto dinámico):

```python
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### 6. Desplegar

1. Click en **"Create Web Service"**
2. Render comenzará a construir y desplegar automáticamente
3. Espera 5-10 minutos para el primer despliegue
4. Verás logs en tiempo real del proceso

### 7. Verificar Despliegue

Una vez completado, Render te dará una URL como:
```
https://dashboard-ventas.onrender.com
```

Visita esa URL para verificar que el dashboard funciona correctamente.

## 🔧 Comandos Útiles

### Ver logs en tiempo real:
```bash
# Desde la interfaz de Render, ve a la pestaña "Logs"
```

### Redesplegar manualmente:
```bash
# En Render, click en "Manual Deploy" → "Deploy latest commit"
```

### Actualizar el código:
```bash
git add .
git commit -m "Actualización"
git push origin main
# Render desplegará automáticamente
```

## ⚠️ Consideraciones Importantes

### 1. Plan Free de Render:
- La app se "duerme" después de 15 minutos de inactividad
- Primera carga tras dormir puede tomar 30-60 segundos
- 750 horas gratis al mes (suficiente para 1 app 24/7)

### 2. Caché:
- El directorio `__pycache__/dashboard_cache` se borrará en cada despliegue
- Considera usar Redis o base de datos para caché persistente

### 3. Archivos estáticos:
- Los archivos en `/static` y `/templates` se despliegan automáticamente

### 4. Credenciales:
- **NUNCA** hagas commit de `.env` o `credentials.json`
- Usa solo variables de entorno en Render

## 🔐 Seguridad

### Recomendaciones:

1. **Rotar SECRET_KEY** en producción
2. **Usar HTTPS** (Render lo provee automáticamente)
3. **Limitar ADMIN_USERS** a correos corporativos
4. **Revisar logs** regularmente por accesos sospechosos
5. **Mantener dependencias actualizadas**:
   ```bash
   pip list --outdated
   pip install -U <paquete>
   ```

## 📊 Monitoreo

### Métricas disponibles en Render:

- CPU usage
- Memory usage
- Request count
- Response time
- Error rate

Ve a **Metrics** en el panel de Render para ver estadísticas.

## 🆘 Troubleshooting

### Error: "Application failed to start"
- Verifica que `gunicorn` esté en `requirements.txt`
- Revisa logs para ver el error específico
- Verifica que `app:app` apunte correctamente a tu instancia Flask

### Error: "Module not found"
- Ejecuta `pip freeze > requirements.txt` localmente
- Asegúrate de incluir todos los paquetes necesarios

### Error: Google Sheets no conecta
- Verifica que `GOOGLE_CREDENTIALS_JSON` esté correctamente configurado
- Asegúrate de que el Service Account tenga acceso a la hoja

### Error: Odoo no conecta
- Verifica las credenciales en variables de entorno
- Asegura que `ODOO_URL` incluya `https://`
- Confirma que la base de datos y usuario son correctos

## 🔄 Despliegue Continuo

Una vez configurado, cada `git push` a `main` desplegará automáticamente:

```bash
# Flujo de trabajo típico:
git add .
git commit -m "Nueva funcionalidad"
git push origin main
# Render detecta el cambio y despliega automáticamente (2-5 min)
```

## 📞 Soporte

- **Documentación Render:** https://render.com/docs
- **Status Page:** https://status.render.com
- **Community Forum:** https://community.render.com

---

**Nota:** Si encuentras algún problema específico, revisa los logs en Render (pestaña "Logs") - ahí encontrarás información detallada sobre cualquier error.
