/**
 * API Endpoint: Model Status
 * 
 * Consulta el estado actual de los modelos sin descargarlos nuevamente
 * Útil para monitoreo y debugging
 */

const MLModel = require('../src/ml-model');

// Instancia global para mantener el estado
let globalMLModel = null;

module.exports = async (req, res) => {
  try {
    // Si no existe instancia, crear una
    if (!globalMLModel) {
      globalMLModel = new MLModel();
      
      // Intentar cargar modelos si están vacíos
      if (Object.keys(globalMLModel.models).length === 0) {
        console.log('📥 No hay modelos en caché, descargando...');
        await globalMLModel.downloadModelsFromDrive();
      }
    }
    
    const info = globalMLModel.getModelInfo();
    
    // Calcular tiempo desde última actualización
    let timeSinceUpdate = null;
    if (info.lastUpdate) {
      const minutes = Math.floor((Date.now() - new Date(info.lastUpdate)) / 60000);
      timeSinceUpdate = `${minutes} minutos`;
    }
    
    // Verificar si necesita actualización
    const needsRefresh = await globalMLModel.shouldRefreshModels();
    
    res.status(200).json({
      success: true,
      status: {
        modelsLoaded: info.totalModels > 0,
        totalModels: info.totalModels,
        lastUpdate: info.lastUpdate,
        timeSinceUpdate: timeSinceUpdate,
        needsRefresh: needsRefresh,
        metadata: info.metadata ? {
          lastTraining: info.metadata.last_update,
          trainingConfig: info.metadata.training_config
        } : null
      },
      models: info.models,
      actions: {
        refresh: '/api/refresh-models',
        status: '/api/model-status',
        trade: '/api/trade'
      },
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Error consultando estado:', error);
    
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
};
