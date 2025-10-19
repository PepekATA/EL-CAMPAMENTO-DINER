const { google } = require('googleapis');
const axios = require('axios');

class MLModel {
  constructor() {
    this.models = {};
    this.lastUpdate = null;
    this.metadata = null;
  }

  async authenticate() {
    try {
      const credentials = JSON.parse(process.env.GOOGLE_DRIVE_CREDENTIALS);
      const auth = new google.auth.GoogleAuth({
        credentials: credentials,
        scopes: ['https://www.googleapis.com/auth/drive.readonly']
      });
      return await auth.getClient();
    } catch (error) {
      console.error('Error autenticando con Google Drive:', error);
      throw error;
    }
  }

  async loadMetadata() {
    try {
      // Cargar metadatos desde el repositorio
      const response = await axios.get(
        `https://raw.githubusercontent.com/${process.env.GITHUB_REPO}/main/models_metadata.json`
      );
      this.metadata = response.data;
      console.log(`📊 Metadatos cargados: ${this.metadata.models.length} modelos disponibles`);
      return this.metadata;
    } catch (error) {
      console.error('Error cargando metadatos:', error);
      return null;
    }
  }

  async downloadModelsFromDrive() {
    try {
      // Primero cargar metadatos
      await this.loadMetadata();
      
      const auth = await this.authenticate();
      const drive = google.drive({ version: 'v3', auth });
      const folderId = process.env.GOOGLE_DRIVE_FOLDER_ID;

      // Listar archivos en la carpeta
      const response = await drive.files.list({
        q: `'${folderId}' in parents and mimeType='application/json' and trashed=false`,
        fields: 'files(id, name, modifiedTime)',
        orderBy: 'modifiedTime desc'
      });

      const files = response.data.files;
      console.log(`📁 Archivos encontrados en Drive: ${files.length}`);
      
      for (const file of files) {
        try {
          // Descargar cada modelo
          const fileData = await drive.files.get({
            fileId: file.id,
            alt: 'media'
          }, { responseType: 'json' });

          const symbol = file.name.replace('_model.json', '').replace('_', '/');
          
          this.models[symbol] = {
            data: fileData.data,
            lastModified: file.modifiedTime,
            fileName: file.name
          };
          
          console.log(`✅ Modelo cargado: ${symbol} (${fileData.data.algorithm})`);
        } catch (error) {
          console.error(`Error descargando ${file.name}:`, error.message);
        }
      }

      this.lastUpdate = new Date();
      console.log(`🔄 Modelos actualizados: ${Object.keys(this.models).join(', ')}`);
      return this.models;
      
    } catch (error) {
      console.error('Error descargando modelos de Drive:', error);
      return this.models;
    }
  }

  async shouldRefreshModels() {
    if (!this.lastUpdate) return true;
    
    // Actualizar cada 30 minutos
    const minutesSinceUpdate = (Date.now() - this.lastUpdate) / (1000 * 60);
    return minutesSinceUpdate > 30;
  }

  async getPrediction(symbol, currentPrice, historicalData) {
    // Refrescar modelos si es necesario
    if (await this.shouldRefreshModels()) {
      await this.downloadModelsFromDrive();
    }

    const model = this.models[symbol];
    
    if (!model) {
      console.log(`⚠️ No hay modelo para ${symbol}, usando estrategia básica`);
      return this.basicStrategy(currentPrice, historicalData);
    }

    // Usar datos del modelo entrenado
    const modelData = model.data;
    const performance = modelData.performance || 0;
    
    // Calcular indicadores
    const indicators = this.calculateIndicators(historicalData);
    
    // Lógica de decisión basada en el modelo
    let action = 'hold';
    let confidence = 0.5;
    
    // Si el modelo tiene buen performance, confiar más en señales
    if (performance > 0.1) { // 10% o más de retorno en entrenamiento
      if (indicators.rsi < 30 && indicators.priceChange < -0.02) {
        action = 'buy';
        confidence = 0.7 + (performance * 0.3);
      } else if (indicators.rsi > 70 && indicators.priceChange > 0.015) {
        action = 'sell';
        confidence = 0.7 + (performance * 0.3);
      }
    }

    return {
      action: action,
      confidence: confidence,
      targetPrice: currentPrice * 1.015, // 1.5% ganancia
      modelPerformance: performance,
      algorithm: modelData.algorithm,
      trainedAt: modelData.trained_at
    };
  }

  calculateIndicators(historicalData) {
    if (!historicalData || historicalData.length < 2) {
      return { rsi: 50, priceChange: 0 };
    }

    const prices = historicalData.slice(-14);
    const currentPrice = prices[prices.length - 1];
    const previousPrice = prices[prices.length - 2];
    
    // RSI simplificado
    let gains = 0;
    let losses = 0;
    
    for (let i = 1; i < prices.length; i++) {
      const change = prices[i] - prices[i - 1];
      if (change > 0) gains += change;
      else losses -= change;
    }
    
    const avgGain = gains / prices.length;
    const avgLoss = losses / prices.length;
    const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
    const rsi = 100 - (100 / (1 + rs));
    
    const priceChange = (currentPrice - previousPrice) / previousPrice;
    
    return { rsi, priceChange };
  }

  basicStrategy(currentPrice, historicalData) {
    const indicators = this.calculateIndicators(historicalData);
    
    if (indicators.rsi < 35 && indicators.priceChange < -0.015) {
      return { 
        action: 'buy', 
        confidence: 0.6, 
        targetPrice: currentPrice * 1.015,
        modelPerformance: 0,
        algorithm: 'basic'
      };
    } else if (indicators.rsi > 65 && indicators.priceChange > 0.015) {
      return { 
        action: 'sell', 
        confidence: 0.6, 
        targetPrice: currentPrice,
        modelPerformance: 0,
        algorithm: 'basic'
      };
    }

    return { 
      action: 'hold', 
      confidence: 0.4, 
      targetPrice: currentPrice,
      modelPerformance: 0,
      algorithm: 'basic'
    };
  }

  getModelInfo() {
    return {
      totalModels: Object.keys(this.models).length,
      lastUpdate: this.lastUpdate,
      metadata: this.metadata,
      models: Object.entries(this.models).map(([symbol, model]) => ({
        symbol,
        algorithm: model.data.algorithm,
        performance: model.data.performance,
        trainedAt: model.data.trained_at
      }))
    };
  }
}

module.exports = MLModel;
