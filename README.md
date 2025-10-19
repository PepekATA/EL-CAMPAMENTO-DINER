# Bot de Trading Automático con Alpaca

Bot de trading automatizado que opera 24/7 con criptomonedas usando la API de Alpaca, estrategia de scalping y Machine Learning.

## Características

- ✅ Trading automatizado 24/7 con criptomonedas
- ✅ Estrategia de scalping (ganancias pequeñas pero constantes)
- ✅ Integración con modelos de Machine Learning desde Google Drive
- ✅ Diversificación automática del portafolio
- ✅ Stop loss y take profit automáticos
- ✅ Desplegado en Vercel con ejecución cada 5 minutos

## Instalación

1. **Clonar repositorio:**
```bash
git clone https://github.com/TU-USUARIO/trading-bot.git
cd trading-bot
```

2. **Instalar dependencias:**
```bash
npm install
```

3. **Configurar variables de entorno:**

En Vercel, agregar estas variables:
- `ALPACA_API_KEY`: Tu API key de Alpaca
- `ALPACA_SECRET_KEY`: Tu secret key de Alpaca
- `GOOGLE_DRIVE_CREDENTIALS`: Credenciales JSON de Google Service Account
- `GOOGLE_DRIVE_FOLDER_ID`: ID de la carpeta donde están los modelos

## Despliegue en Vercel
```bash
vercel --prod
```

## Endpoints

- `/api/trade` - Ejecuta el bot de trading (cron cada 5 min)
- `/api/status` - Estado actual del bot
- `/api/train` - Actualiza modelos desde Google Drive

## Configuración de Google Drive

1. Crear un Service Account en Google Cloud
2. Habilitar Google Drive API
3. Compartir carpeta de modelos con el email del Service Account
4. Guardar credenciales JSON en variable de entorno

## ⚠️ IMPORTANTE

- El bot usa la cuenta PAPER de Alpaca por defecto (simulación)
- Para usar dinero real, cambiar `paper: false` en `src/alpaca.js`
- Monitorear el bot regularmente
- Comenzar con capital pequeño para pruebas

## Licencia

MIT
