# 🤖 Trading Bot - Guía Completa de Configuración

## 🎯 Arquitectura del Sistema

```
Google Colab (Entrenamiento)
       ↓
Google Drive (Almacena modelos .json)
       ↓
GitHub (Actualiza models_metadata.json)
       ↓
Vercel (Backend API + Auto-deploy)
       ↓
Streamlit Cloud (Dashboard en vivo)
       ↓
Alpaca (Ejecuta trades reales)
```

---

## 📋 Requisitos Previos

### 1. Cuenta de Alpaca
1. Crear cuenta en: https://alpaca.markets
2. Obtener API Keys (Paper Trading):
   - **API Key ID**
   - **Secret Key**
3. ⚠️ **Importante**: Usar cuenta PAPER primero para pruebas

### 2. Cuenta de Google
- Gmail activa (para Google Drive y Colab)
- Espacio en Drive: ~100MB para modelos

### 3. Cuenta de GitHub
1. Crear repositorio: `trading-bot`
2. Hacer público o privado (tu elección)
3. Crear Personal Access Token:
   - Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Permisos: `repo` (todos los sub-permisos)
   - Guardar el token: `ghp_xxxxxxxxxxxxx`

### 4. Cuenta de Vercel
1. Registrarse en: https://vercel.com
2. Conectar con tu cuenta de GitHub
3. Importar tu repositorio `trading-bot`

### 5. Cuenta de Streamlit Cloud
1. Registrarse en: https://share.streamlit.io
2. Conectar con tu cuenta de GitHub
3. Preparar para desplegar

---

## 🚀 Configuración Paso a Paso

### PASO 1: Configurar Google Drive API

1. **Ir a Google Cloud Console**
   - https://console.cloud.google.com

2. **Crear nuevo proyecto**
   - Nombre: `Trading Bot`

3. **Habilitar Google Drive API**
   - APIs & Services → Library
   - Buscar "Google Drive API"
   - Habilitar

4. **Crear Service Account**
   - APIs & Services → Credentials
   - Create Credentials → Service Account
   - Nombre: `trading-bot-service`
   - Role: `Basic → Editor`

5. **Generar clave JSON**
   - Click en la service account creada
   - Keys → Add Key → Create new key → JSON
   - Descargar el archivo JSON

6. **Crear carpeta en Drive**
   - Crear carpeta: `TradingBot/models`
   - Click derecho → Share
   - Agregar el email de la service account
   - Permiso: `Editor`
   - Copiar el ID de la carpeta (de la URL):
     ```
     https://drive.google.com/drive/folders/AQUI_ESTA_EL_ID
     ```

### PASO 2: Configurar GitHub

1. **Clonar repositorio localmente**
   ```bash
   git clone https://github.com/TU-USUARIO/trading-bot.git
   cd trading-bot
   ```

2. **Copiar todos los archivos del proyecto**
   - Todos los archivos `.js` en carpetas `api/` y `src/`
   - `package.json`
   - `vercel.json`
   - `app.py`
   - `requirements.txt`
   - `.streamlit/config.toml`
   - `utils/` (todos los archivos Python)
   - `.github/workflows/sync-models.yml`

3. **Crear archivo `.gitignore`**
   ```
   node_modules/
   .env
   .DS_Store
   *.log
   __pycache__/
   .vercel
   ```

4. **Commit y push**
   ```bash
   git add .
   git commit -m "🚀 Initial bot setup"
   git push origin main
   ```

### PASO 3: Configurar Vercel

1. **Importar proyecto desde GitHub**
   - New Project → Import tu repositorio

2. **Configurar variables de entorno**
   - Settings → Environment Variables
   - Agregar las siguientes:

   ```env
   # Alpaca API
   ALPACA_API_KEY=tu_alpaca_api_key_aqui
   ALPACA_SECRET_KEY=tu_alpaca_secret_key_aqui
   
   # Google Drive (pegar TODO el contenido del JSON descargado)
   GOOGLE_DRIVE_CREDENTIALS={"type":"service_account","project_id":"..."}
   
   # Google Drive Folder ID (el ID que copiaste)
   GOOGLE_DRIVE_FOLDER_ID=1a2b3c4d5e6f7g8h9i
   
   # GitHub Repo (formato: usuario/repositorio)
   GITHUB_REPO=tu-usuario/trading-bot
   ```

3. **Crear Deploy Hook** (para GitHub Actions)
   - Settings → Git → Deploy Hooks
   - Create Hook
   - Copiar la URL generada
   - Guardarla para el siguiente paso

4. **Deploy**
   - Deploy → Vercel detectará `vercel.json` automáticamente
   - Esperar a que termine el deployment
   - Anotar la URL: `https://tu-bot.vercel.app`

### PASO 4: Configurar GitHub Actions

1. **Agregar secrets en GitHub**
   - Tu repositorio → Settings → Secrets and variables → Actions
   - New repository secret:

   ```
   VERCEL_DEPLOY_HOOK=la_url_del_deploy_hook_que_copiaste
   ```

2. **Verificar workflow**
   - El archivo `.github/workflows/sync-models.yml` ya debe estar en tu repo
   - Actions → Verificar que aparece el workflow

### PASO 5: Configurar Streamlit Cloud

1. **Desplegar app**
   - https://share.streamlit.io
   - New app
   - Repository: `tu-usuario/trading-bot`
   - Branch: `main`
   - Main file path: `app.py`

2. **Configurar Secrets**
   - Advanced settings → Secrets
   - Pegar esto y modificar con tus valores:

   ```toml
   # Secrets para Streamlit Cloud
   VERCEL_API_URL = "https://tu-bot.vercel.app"
   ALPACA_API_KEY = "tu_alpaca_api_key"
   ALPACA_SECRET_KEY = "tu_alpaca_secret_key"
   ```

3. **Deploy**
   - Save → Deploy
   - Esperar 2-3 minutos
   - Tu dashboard estará en: `https://share.streamlit.io/tu-usuario/trading-bot`

### PASO 6: Ejecutar Entrenamiento en Google Colab

1. **Abrir Google Colab**
   - https://colab.research.google.com

2. **Crear nuevo notebook**
   - File → New notebook

3. **Copiar el código del notebook de entrenamiento**
   - Copiar TODO el código del artifact "Trading Bot - Colab Training Notebook"

4. **Configurar las variables** (al inicio del notebook)
   ```python
   ALPACA_API_KEY = "tu_alpaca_api_key"
   ALPACA_SECRET_KEY = "tu_alpaca_secret_key"
   GITHUB_TOKEN = "ghp_tu_token_de_github"
   GITHUB_REPO = "tu-usuario/trading-bot"
   DRIVE_FOLDER = "/content/drive/MyDrive/TradingBot/models"
   ```

5. **Ejecutar todas las celdas**
   - Runtime → Run all
   - Autorizar Google Drive cuando lo pida
   - Esperar 10-15 minutos (primera vez)

6. **Verificar resultados**
   - Ver modelos en Google Drive
   - Ver `models_metadata.json` en GitHub
   - Ver actualización en Vercel logs
   - Ver nuevos modelos en Streamlit dashboard

---

## ✅ Verificación del Sistema

### 1. Test de APIs de Vercel

```bash
# Status del bot
curl https://tu-bot.vercel.app/api/status

# Estado de modelos
curl https://tu-bot.vercel.app/api/model-status

# Refrescar modelos manualmente
curl https://tu-bot.vercel.app/api/refresh-models

# Ejecutar trade manual
curl https://tu-bot.vercel.app/api/trade
```

### 2. Verificar Logs

**Vercel:**
- https://vercel.com/tu-usuario/trading-bot/logs
- Buscar: "Modelos actualizados desde Google Drive"

**GitHub Actions:**
- Tu repo → Actions
- Verificar que el workflow "Sync Trading Models" se ejecutó

**Streamlit:**
- Abrir dashboard
- Debe mostrar datos de Alpaca
- Tab "ML Models" debe mostrar modelos entrenados

### 3. Verificar Cron Jobs

**En Vercel:**
- Settings → Cron Jobs
- Debe haber 2 jobs:
  - `/api/trade` - cada 5 minutos
  - `/api/refresh-models` - cada 30 minutos

---

## 🔄 Flujo de Trabajo Diario

### Automático (sin intervención)
1. **Cada 5 minutos**: Bot ejecuta estrategia de trading
2. **Cada 30 minutos**: Bot descarga modelos actualizados de Drive
3. **Cada hora**: GitHub Actions verifica cambios
4. **Dashboard**: Se actualiza cada 30 segundos

### Manual (cuando quieras reentrenar)
1. Abrir Google Colab
2. Ejecutar notebook de entrenamiento
3. Modelos se guardan en Drive
4. GitHub se actualiza automáticamente
5. Vercel redeploya automáticamente
6. Streamlit muestra nuevos modelos

---

## 🐛 Troubleshooting

### Error: "No se encontraron modelos"
**Solución:**
1. Verificar que el notebook de Colab se ejecutó completamente
2. Revisar Google Drive: debe haber archivos `.json` en la carpeta
3. Verificar `GOOGLE_DRIVE_FOLDER_ID` en Vercel
4. Verificar que la carpeta está compartida con el service account

### Error: "Authentication failed"
**Solución:**
1. Verificar `GOOGLE_DRIVE_CREDENTIALS` en Vercel (JSON completo)
2. Verificar que service account tiene permisos en la carpeta
3. Recrear service account si es necesario

### Error: "GitHub update failed"
**Solución:**
1. Verificar `GITHUB_TOKEN` tiene permisos `repo`
2. Verificar formato de `GITHUB_REPO`: `usuario/repositorio`
3. Generar nuevo token si expiró

### Dashboard no muestra datos
**Solución:**
1. Verificar secrets en Streamlit Cloud
2. Verificar que Vercel está respondiendo: `curl https://tu-bot.vercel.app/api/status`
3. Ver logs en Streamlit Cloud: Settings → Logs
4. Verificar credenciales de Alpaca

### Bot no ejecuta trades
**Solución:**
1. Verificar cuenta de Alpaca está activa
2. Revisar logs en Vercel
3. Ejecutar manualmente: `curl https://tu-bot.vercel.app/api/trade`
4. Verificar que hay modelos cargados: `/api/model-status`

---

## 📊 Monitoreo

### URLs Importantes

- **Dashboard Live**: `https://share.streamlit.io/tu-usuario/trading-bot`
- **API Backend**: `https://tu-bot.vercel.app`
- **GitHub Repo**: `https://github.com/tu-usuario/trading-bot`
- **Vercel Logs**: `https://vercel.com/tu-usuario/trading-bot/logs`
- **Alpaca Dashboard**: `https://app.alpaca.markets`

### Métricas a Monitorear

1. **Performance del Bot**
   - Equity total
   - Ganancias/Pérdidas diarias
   - Número de trades
   - Win rate

2. **Performance de Modelos**
   - Accuracy de predicciones
   - Returns por modelo
   - Modelos más/menos utilizados

3. **Sistema**
   - Uptime de Vercel
   - Errores en logs
   - Tiempo de respuesta API
   - Actualización de modelos

---

## 🎓 Próximos Pasos

### Mejoras Recomendadas

1. **Agregar notificaciones**
   - Email cuando hay trades
   - Telegram bot para alertas
   - Discord webhook

2. **Mejorar estrategia**
   - Backtesting más robusto
   - Más indicadores técnicos
   - Optimización de hiperparámetros

3. **Dashboard avanzado**
   - Gráficas de equity histórico
   - Análisis de drawdown
   - Comparación con benchmarks

4. **Seguridad**
   - Rate limiting en APIs
   - Autenticación en endpoints
   - Encriptación de credenciales

---

## ⚠️ IMPORTANTE - SEGURIDAD

1. **NUNCA** hacer commit de:
   - API keys
   - Tokens de GitHub
   - Credenciales de Google

2. **Usar cuenta PAPER** de Alpaca para pruebas

3. **Empezar con capital pequeño** cuando vayas a real

4. **Monitorear diariamente** el bot

5. **Tener stop-loss** configurado

---

## 📞 Soporte

Si tienes problemas:

1. Revisar esta guía completa
2. Verificar logs en Vercel y Streamlit
3. Revisar GitHub Actions
4. Probar endpoints manualmente con `curl`
5. Verificar que todas las credenciales son correctas

---

## 🎉 ¡Listo!

Tu bot de trading está configurado y funcionando 24/7:

✅ Entrenar modelos en Google Colab
✅ Guardar automáticamente en Google Drive  
✅ Sincronizar con GitHub
✅ Desplegar en Vercel
✅ Dashboard en vivo en Streamlit
✅ Trading automático cada 5 minutos
✅ Actualización de modelos cada 30 minutos

**¡A ganar dinero! 💰🚀**
