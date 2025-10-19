const { google } = require('googleapis');
const axios = require('axios');

class MLModel {
  constructor() {
    this.models = {};
    this.lastUpdate = null;
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

  async downloadModelsFromDrive() {
    try {
      const auth = await this.authenticate();
      const drive = google.drive({ version: 'v3', auth });
      const folderId = process.env.GOOGLE_DRIVE_FOLDER_ID;

      // Listar archivos en la carpeta
      const response = await drive.files.list({
        q: `'${folderId}' in parents and mimeType='application/json'`,
        fields: 'files(id, name, modifiedTime)'
      });

      const files = response.data.files;
      
      for (const file of files) {
        // Descargar cada modelo
        const fileData = await drive.files.get({
          fileId: file.id,
          alt: 'media'
        }, { responseType: 'json' });

        const symbol = file.name.replace('.json', '');
        this.models[symbol] = {
          data: fileData.data,
          lastModified: file.modifiedTime
        };
      }

      this.lastUpdate = new Date();
      console.log(`Modelos actualizados: ${Object.keys(this.models).join(', ')}`);
      return this.models;
    } catch (error) {
      console.error('Error descargando modelos de Drive:', error);
      return this.models;
    }
  }

  async shouldRefreshModels() {
    if (!this.lastUpdate) return true;
    
    const hoursSinceUpdate = (Date.now() - this.lastUpdate) / (1000 * 60 * 60);
    return hoursSinceUpdate > 1; // Actualizar cada hora
  }

  async getPrediction(symbol, currentPrice, historicalData) {
    if (await this.shouldRefreshModels()) {
      await this.downloadModelsFromDrive();
    }

    const model = this.models[symbol];
    if (!model) {
      console.log(`No hay modelo para ${symbol}, usando estrategia básica`);
      return this.basicStrategy(currentPrice, historicalData);
    }

    // Aquí implementarías la lógica del modelo ML
    // Por ahora, simulación simple
    return {
      action: 'hold', // 'buy', 'sell', 'hold'
      confidence: 0.5,
      targetPrice: currentPrice * 1.02 // 2% ganancia objetivo
    };
  }

  basicStrategy(currentPrice, historicalData) {
    // Estrategia básica cuando no hay modelo
    if (historicalData.length < 2) {
      return { action: 'hold', confidence: 0, targetPrice: currentPrice };
    }

    const avgPrice = historicalData.reduce((a, b) => a + b, 0) / historicalData.length;
    const priceChange = (currentPrice - avgPrice) / avgPrice;

    if (priceChange < -0.01) { // Precio bajo 1%
      return { action: 'buy', confidence: 0.6, targetPrice: currentPrice * 1.015 };
    } else if (priceChange > 0.015) { // Precio alto 1.5%
      return { action: 'sell', confidence: 0.6, targetPrice: currentPrice };
    }

    return { action: 'hold', confidence: 0.4, targetPrice: currentPrice };
  }
}

module.exports = MLModel;
