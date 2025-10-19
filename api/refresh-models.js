/**
 * API Endpoint: Refresh Models
 * 
 * Este endpoint descarga y actualiza los modelos de ML desde Google Drive
 * Se ejecuta automáticamente cada 30 minutos via cron job en Vercel
 * También puede ser llamado manualmente
 * 
 * Flujo:
 * 1. Conecta con Google Drive usando credenciales
 * 2. Descarga los modelos entrenados en Colab
 * 3. Carga los metadatos desde GitHub
 * 4. Actualiza la caché de modelos en memoria
 * 5. Retorna información sobre los modelos cargados
 */

const MLModel = require('../src/ml-model');

module.exports = async (req, res) => {
  const startTime = Date.now();
  
  try {
    console.log('🔄 Iniciando actualización de modelos...');
    console.log(`📅 Timestamp: ${new Date().toISOString()}`);
    
    // Crear instancia del gestor de modelos ML
    const mlModel = new MLModel();
    
    // Paso 1: Descargar modelos desde Google Drive
    console.log('📥 Descargando modelos desde Google Drive...');
    const models = await mlModel.downloadModelsFromDrive();
    
    if (!models || Object.keys(models).length === 0) {
      console.warn('⚠️ No se encontraron modelos en Google Drive');
      return res.status(200).json({
        success: true,
        warning: 'No se encontraron modelos en Google Drive',
        modelsCount: 0,
        timestamp: new Date().toISOString(),
        executionTime: `${Date.now() - startTime}ms`
      });
    }
    
    // Paso 2: Obtener información detallada de los modelos
    console.log('📊 Recopilando información de modelos...');
    const modelInfo = mlModel.getModelInfo();
    
    // Paso 3: Validar integridad de los modelos
    const validationResults = validateModels(modelInfo.models);
    
    // Calcular estadísticas
    const stats = calculateStats(modelInfo.models);
    
    // Logging detallado
    console.log('✅ Modelos actualizados exitosamente:');
    console.log(`   - Total de modelos: ${modelInfo.totalModels}`);
    console.log(`   - Última actualización: ${modelInfo.lastUpdate}`);
    console.log(`   - Performance promedio: ${stats.avgPerformance.toFixed(2)}%`);
    console.log(`   - Mejor modelo: ${stats.bestModel?.symbol} (${stats.bestModel?.performance.toFixed(2)}%)`);
    
    const executionTime = Date.now() - startTime;
    console.log(`⏱️ Tiempo de ejecución: ${executionTime}ms`);
    
    // Respuesta exitosa
    res.status(200).json({
      success: true,
      message: 'Modelos actualizados correctamente desde Google Drive',
      data: {
        modelsCount: modelInfo.totalModels,
        lastUpdate: modelInfo.lastUpdate,
        metadata: modelInfo.metadata,
        models: modelInfo.models.map(model => ({
          symbol: model.symbol,
          algorithm: model.algorithm,
          performance: `${(model.performance * 100).toFixed(2)}%`,
          trainedAt: model.trainedAt,
          status: validationResults[model.symbol] ? 'valid' : 'invalid'
        })),
        statistics: {
          totalModels: stats.totalModels,
          averagePerformance: `${stats.avgPerformance.toFixed(2)}%`,
          bestPerformance: `${stats.bestPerformance.toFixed(2)}%`,
          worstPerformance: `${stats.worstPerformance.toFixed(2)}%`,
          bestModel: stats.bestModel,
          algorithms: stats.algorithms
        },
        validation: {
          allValid: Object.values(validationResults).every(v => v),
          results: validationResults
        }
      },
      executionTime: `${executionTime}ms`,
      timestamp: new Date().toISOString(),
      nextUpdate: getNextUpdateTime()
    });
    
  } catch (error) {
    console.error('❌ Error actualizando modelos:', error);
    console.error('Stack trace:', error.stack);
    
    // Respuesta de error detallada
    res.status(500).json({
      success: false,
      error: {
        message: error.message,
        type: error.name,
        details: process.env.NODE_ENV === 'development' ? error.stack : undefined
      },
      timestamp: new Date().toISOString(),
      executionTime: `${Date.now() - startTime}ms`,
      troubleshooting: {
        commonIssues: [
          'Verificar credenciales de Google Drive en variables de entorno',
          'Confirmar que GOOGLE_DRIVE_FOLDER_ID es correcto',
          'Verificar que la carpeta de Drive está compartida con la cuenta de servicio',
          'Revisar que los archivos .json existen en la carpeta de Drive',
          'Confirmar que GITHUB_REPO está en formato correcto: usuario/repositorio'
        ],
        documentation: 'https://github.com/tu-usuario/trading-bot#troubleshooting'
      }
    });
  }
};

/**
 * Validar integridad de los modelos
 */
function validateModels(models) {
  const validation = {};
  
  for (const model of models) {
    const isValid = 
      model.symbol && 
      model.algorithm && 
      typeof model.performance === 'number' &&
      model.trainedAt &&
      !isNaN(new Date(model.trainedAt).getTime());
    
    validation[model.symbol] = isValid;
    
    if (!isValid) {
      console.warn(`⚠️ Modelo inválido detectado: ${model.symbol}`);
    }
  }
  
  return validation;
}

/**
 * Calcular estadísticas de los modelos
 */
function calculateStats(models) {
  if (!models || models.length === 0) {
    return {
      totalModels: 0,
      avgPerformance: 0,
      bestPerformance: 0,
      worstPerformance: 0,
      bestModel: null,
      algorithms: {}
    };
  }
  
  const performances = models.map(m => m.performance * 100);
  const avgPerformance = performances.reduce((a, b) => a + b, 0) / performances.length;
  const bestPerformance = Math.max(...performances);
  const worstPerformance = Math.min(...performances);
  const bestModel = models.find(m => m.performance * 100 === bestPerformance);
  
  // Contar algoritmos
  const algorithms = {};
  models.forEach(model => {
    algorithms[model.algorithm] = (algorithms[model.algorithm] || 0) + 1;
  });
  
  return {
    totalModels: models.length,
    avgPerformance,
    bestPerformance,
    worstPerformance,
    bestModel: bestModel ? {
      symbol: bestModel.symbol,
      performance: bestPerformance,
      algorithm: bestModel.algorithm
    } : null,
    algorithms
  };
}

/**
 * Calcular próxima actualización (en 30 minutos)
 */
function getNextUpdateTime() {
  const next = new Date();
  next.setMinutes(next.getMinutes() + 30);
  return next.toISOString();
}

/**
 * Middleware para logging de requests (opcional)
 */
function logRequest(req) {
  console.log('📝 Request Info:');
  console.log(`   - Method: ${req.method}`);
  console.log(`   - URL: ${req.url}`);
  console.log(`   - User-Agent: ${req.headers['user-agent']}`);
  console.log(`   - IP: ${req.headers['x-forwarded-for'] || req.connection.remoteAddress}`);
}
