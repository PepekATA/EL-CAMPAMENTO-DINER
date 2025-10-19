const Alpaca = require('@alpacahq/alpaca-trade-api');

class AlpacaClient {
  constructor() {
    this.alpaca = new Alpaca({
      keyId: process.env.ALPACA_API_KEY,
      secretKey: process.env.ALPACA_SECRET_KEY,
      paper: true, // Cambiar a false para cuenta real
      usePolygon: false
    });
  }

  async getAccount() {
    try {
      return await this.alpaca.getAccount();
    } catch (error) {
      console.error('Error obteniendo cuenta:', error);
      throw error;
    }
  }

  async getPositions() {
    try {
      return await this.alpaca.getPositions();
    } catch (error) {
      console.error('Error obteniendo posiciones:', error);
      return [];
    }
  }

  async getCryptoPrice(symbol) {
    try {
      const bars = await this.alpaca.getCryptoBars(
        symbol,
        { limit: 1, timeframe: '1Min' }
      );
      return bars[symbol][0].c; // Precio de cierre
    } catch (error) {
      console.error(`Error obteniendo precio de ${symbol}:`, error);
      return null;
    }
  }

  async placeCryptoOrder(symbol, qty, side) {
    try {
      const order = await this.alpaca.createOrder({
        symbol: symbol,
        qty: qty,
        side: side, // 'buy' o 'sell'
        type: 'market',
        time_in_force: 'gtc'
      });
      console.log(`Orden ${side} ejecutada para ${symbol}:`, order);
      return order;
    } catch (error) {
      console.error(`Error ejecutando orden ${side} para ${symbol}:`, error);
      throw error;
    }
  }

  async getOpenOrders() {
    try {
      return await this.alpaca.getOrders({ status: 'open' });
    } catch (error) {
      console.error('Error obteniendo órdenes abiertas:', error);
      return [];
    }
  }

  async cancelAllOrders() {
    try {
      await this.alpaca.cancelAllOrders();
      console.log('Todas las órdenes canceladas');
    } catch (error) {
      console.error('Error cancelando órdenes:', error);
    }
  }
}

module.exports = AlpacaClient;
