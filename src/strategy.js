const AlpacaClient = require('./alpaca');
const MLModel = require('./ml-model');
const PortfolioManager = require('./portfolio');

class TradingStrategy {
  constructor() {
    this.alpaca = new AlpacaClient();
    this.mlModel = new MLModel();
    this.portfolio = new PortfolioManager(this.alpaca);
    this.priceHistory = {};
    this.profitTarget = 0.015; // 1.5% ganancia objetivo (scalping)
    this.stopLoss = 0.01; // 1% stop loss
  }

  async initialize() {
    await this.mlModel.downloadModelsFromDrive();
    console.log('Bot inicializado correctamente');
  }

  async executeScalpingStrategy() {
    try {
      const positions = await this.alpaca.getPositions();
      
      for (const symbol of this.portfolio.targetAssets) {
        await this.processAsset(symbol, positions);
      }

      // Rebalancear portafolio cada 6 horas
      const hour = new Date().getHours();
      if (hour % 6 === 0) {
        await this.portfolio.rebalancePortfolio();
      }

    } catch (error) {
      console.error('Error ejecutando estrategia:', error);
    }
  }

  async processAsset(symbol, positions) {
    try {
      const currentPrice = await this.alpaca.getCryptoPrice(symbol);
      if (!currentPrice) return;

      // Actualizar historial de precios
      if (!this.priceHistory[symbol]) {
        this.priceHistory[symbol] = [];
      }
      this.priceHistory[symbol].push(currentPrice);
      if (this.priceHistory[symbol].length > 100) {
        this.priceHistory[symbol].shift();
      }

      const position = positions.find(p => p.symbol === symbol);

      if (position) {
        // Ya tenemos posición - evaluar venta
        await this.evaluateSell(symbol, position, currentPrice);
      } else {
        // No tenemos posición - evaluar compra
        await this.evaluateBuy(symbol, currentPrice);
      }

    } catch (error) {
      console.error(`Error procesando ${symbol}:`, error);
    }
  }

  async evaluateBuy(symbol, currentPrice) {
    const prediction = await this.mlModel.getPrediction(
      symbol,
      currentPrice,
      this.priceHistory[symbol] || []
    );

    if (prediction.action === 'buy' && prediction.confidence > 0.5) {
      const account = await this.alpaca.getAccount();
      const buyingPower = parseFloat(account.buying_power);
      const maxInvestment = buyingPower / this.portfolio.targetAssets.length * 0.9;

      const qty = (maxInvestment / currentPrice).toFixed(8);

      console.log(`🟢 SEÑAL DE COMPRA: ${symbol} a $${currentPrice} (Confianza: ${prediction.confidence})`);
      await this.alpaca.placeCryptoOrder(symbol, qty, 'buy');
    }
  }

  async evaluateSell(symbol, position, currentPrice) {
    const avgEntryPrice = parseFloat(position.avg_entry_price);
    const profitPercent = (currentPrice - avgEntryPrice) / avgEntryPrice;

    // Vender si alcanzamos objetivo de ganancia
    if (profitPercent >= this.profitTarget) {
      console.log(`💰 TOMANDO GANANCIA: ${symbol} +${(profitPercent * 100).toFixed(2)}%`);
      await this.alpaca.placeCryptoOrder(symbol, position.qty, 'sell');
      return;
    }

    // Stop loss
    if (profitPercent <= -this.stopLoss) {
      console.log(`🛑 STOP LOSS: ${symbol} ${(profitPercent * 100).toFixed(2)}%`);
      await this.alpaca.placeCryptoOrder(symbol, position.qty, 'sell');
      return;
    }

    // Consultar modelo ML para señal de venta
    const prediction = await this.mlModel.getPrediction(
      symbol,
      currentPrice,
      this.priceHistory[symbol] || []
    );

    if (prediction.action === 'sell' && prediction.confidence > 0.6 && profitPercent > 0) {
      console.log(`📊 SEÑAL ML DE VENTA: ${symbol} +${(profitPercent * 100).toFixed(2)}%`);
      await this.alpaca.placeCryptoOrder(symbol, position.qty, 'sell');
    }
  }

  async getStatus() {
    const account = await this.alpaca.getAccount();
    const positions = await this.alpaca.getPositions();
    
    return {
      equity: account.equity,
      buyingPower: account.buying_power,
      positions: positions.length,
      lastUpdate: this.mlModel.lastUpdate,
      models: Object.keys(this.mlModel.models)
    };
  }
}

module.exports = TradingStrategy;
