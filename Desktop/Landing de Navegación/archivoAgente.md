# Rol del Agente
Actúa como un Desarrollador Senior de Frontend especializado en React y UX Corporativa. Tu objetivo es generar una aplicación web completa, limpia y lista para producción.

# Objetivo del Proyecto
Crear un "Portal de Acceso" (Landing Page) que sirva como hub central para dirigir al CEO a 4 herramientas internas diferentes.

# Stack Tecnológico
- **Framework:** Next.js 14+ (App Router).
- **Estilos:** Tailwind CSS (Usa clases utilitarias para todo el diseño).
- **Iconos:** Lucide-React.
- **Fuente:** Inter o una fuente sans-serif corporativa limpia.
- **Despliegue:** Configurado para desplegarse fácilmente en Render.

# Estructura de Datos
Crea una constante o archivo de configuración `config.ts` que contenga el array de datos para facilitar cambios futuros de URLs. 
Los datos actuales son:

1. **Stock Odoo**
   - Descripción sugerida: "Gestión de inventario y almacenes."
   - Icono sugerido: Box o Package.
2. **Dashboard Ventas Locales**
   - Descripción sugerida: "Métricas y KPIs del mercado nacional."
   - Icono sugerido: MapPin o Store.
3. **Dashboard Ventas Internacionales**
   - Descripción sugerida: "Reportes de exportación y mercados globales."
   - Icono sugerido: Globe o Plane.
4. **Dashboard Dirección**
   - Descripción sugerida: "Visión general ejecutiva y toma de decisiones."
   - Icono sugerido: BarChart o Briefcase.

# Instrucciones de Diseño (UI/UX)
1. **Header:**
   - Debe ser limpio, fondo blanco o gris muy suave.
   - Debe incluir un espacio para el Logo de la empresa (usa un placeholder `<img>` o texto estilizado por ahora).
2. **Contenedor Principal:**
   - Centrado en la pantalla con un `max-width`.
   - Fondo de página en un tono gris muy claro (`bg-slate-50`) para resaltar las tarjetas blancas.
3. **Grid de Tarjetas:**
   - Usa CSS Grid.
   - Móvil: 1 columna.
   - Tablet/Escritorio: 2 columnas (2x2) o 4 en fila dependiendo del ancho, pero 2x2 suele verse mejor centrado.
4. **Diseño de la Tarjeta (Card):**
   - Fondo blanco, borde sutil, sombra suave (`shadow-sm`).
   - Al pasar el mouse (`hover`): La tarjeta debe elevarse ligeramente y la sombra debe intensificarse (`shadow-md`), cambiando el color del borde o del texto al color primario.
   - El clic en la tarjeta debe abrir el link en una nueva pestaña (`target="_blank"`).

# Entregables Esperados
1. Genera la estructura de carpetas necesaria.
2. Proporciona el código para `page.tsx`, `layout.tsx` y cualquier componente necesario (ej: `AppCard.tsx`).
3. Proporciona el código para `tailwind.config.ts` si requiere personalización.
4. Incluye instrucciones breves para ejecutarlo localmente (`npm run dev`) y para construirlo (`npm run build`).

# Nota Importante
El código debe ser modular y "Type Safe" (usa TypeScript interfaces para los objetos de los enlaces).