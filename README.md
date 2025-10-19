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
## 📡 Endpoints API

### 1. `/api/trade`
**Método:** GET/POST  
**Descripción:** Ejecuta el bot de trading con la estrategia de scalping  
**Frecuencia:** Cada 5 minutos (cron automático)  
**Respuesta:**
```json
{
  "success": true,
  "message": "Trading ejecutado correctamente",
  "timestamp": "2025-10-19T10:30:00.000Z",
  "status": {
    "equity": "10245.67",
    "buyingPower": "8532.21",
    "positions": 3,
    "lastUpdate": "2025-10-19T09:00:00.000Z",
    "models": ["BTC/USD", "ETH/USD", "LTC/USD"]
  }
}
```

### 2. `/api/refresh-models`
**Método:** GET/POST  
**Descripción:** Actualiza los modelos ML desde Google Drive  
**Frecuencia:** Cada 30 minutos (cron automático)  
**Manual:** `curl https://tu-bot.vercel.app/api/refresh-models`  
**Respuesta:**
```json
{
  "success": true,
  "message": "Modelos actualizados correctamente",
  "data": {
    "modelsCount": 8,
    "lastUpdate": "2025-10-19T10:00:00.000Z",
    "models": [
      {
        "symbol": "BTC/USD",
        "algorithm": "PPO",
        "performance": "15.32%",
        "trainedAt": "2025-10-19T08:00:00.000Z",
        "status": "valid"
      }
    ],
    "statistics": {
      "averagePerformance": "12.45%",
      "bestPerformance": "18.76%",
      "bestModel": {
        "symbol": "ETH/USD",
        "performance": 18.76
      }
    }
  },
  "nextUpdate": "2025-10-19T10:30:00.000Z"
}
```

### 3. `/api/model-status`
**Método:** GET  
**Descripción:** Consulta el estado actual de los modelos sin actualizarlos  
**Uso:** Monitoreo y debugging  
**Respuesta:**
```json
{
  "success": true,
  "status": {
    "modelsLoaded": true,
    "totalModels": 8,
    "lastUpdate": "2025-10-19T10:00:00.000Z",
    "timeSinceUpdate": "15 minutos",
    "needsRefresh": false
  },
  "models": [...],
  "actions": {
    "refresh": "/api/refresh-models",
    "status": "/api/model-status",
    "trade": "/api/trade"
  }
}
```

### 4. `/api/status`
**Método:** GET  
**Descripción:** Estado general del bot de trading  
**Respuesta:**
```json
{
  "success": true,
  "status": {
    "equity": "10245.67",
    "buyingPower": "8532.21",
    "positions": 3,
    "lastUpdate": "2025-10-19T10:00:00.000Z"
  }
}
```

## 🔧 Testing Manual de Endpoints
```bash
# Refrescar modelos manualmente
curl https://tu-bot.vercel.app/api/refresh-models

# Ver estado de modelos
curl https://tu-bot.vercel.app/api/model-status

# Ejecutar trading manualmente
curl https://tu-bot.vercel.app/api/trade

# Ver estado general
curl https://tu-bot.vercel.app/api/status
```

## 🔄 Flujo de Actualización Automática
```
Google Colab (Entrenamiento)
         ↓
    Google Drive (Guarda modelos .json)
         ↓
    GitHub (Actualiza metadata)
         ↓
    Vercel (Auto-deploy)
         ↓
    /api/refresh-models (Descarga modelos cada 30 min)
         ↓
    /api/trade (Usa modelos actualizados cada 5 min)
```

## ⚙️ Variables de Entorno Requeridas
```bash
# Alpaca Trading
ALPACA_API_KEY=tu_api_key
ALPACA_SECRET_KEY=tu_secret_key

# Google Drive
GOOGLE_DRIVE_CREDENTIALS={"type":"service_account",...}
GOOGLE_DRIVE_FOLDER_ID=1a2b3c4d5e6f

# GitHub
GITHUB_REPO=tu-usuario/trading-bot
```

## 📊 Monitoreo

Para monitorear el bot en tiempo real:

1. **Logs de Vercel:** https://vercel.com/tu-usuario/trading-bot/logs
2. **Estado de modelos:** https://tu-bot.vercel.app/api/model-status
3. **Estado de trading:** https://tu-bot.vercel.app/api/status

## 🐛 Troubleshooting

### Error: "No se encontraron modelos"
- Verificar que el entrenamiento en Colab se ejecutó correctamente
- Confirmar que los archivos .json están en Google Drive
- Verificar `GOOGLE_DRIVE_FOLDER_ID`

### Error: "Authentication failed"
- Verificar `GOOGLE_DRIVE_CREDENTIALS`
- Confirmar que la carpeta está compartida con la Service Account

### Error: "GitHub update failed"
- Verificar `GITHUB_TOKEN` con permisos de escritura
- Confirmar formato de `GITHUB_REPO`: usuario/repositorio
