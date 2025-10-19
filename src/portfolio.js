class PortfolioManager {
  constructor(alpacaClient) {
    this.alpaca = alpacaClient;
    this.targetAssets = [
      'BTC/USD',
      'ETH/USD',
      'LTC/USD',
      'BCH/USD',
      'DOGE/USD'
    ]; // Assets de crypto 24/7
  }

  async diversifyCapital() {
    try {
      const account = await this.alpaca.getAccount();
      const buyingPower = parseFloat(account.buying_power);
      const positions = await this.alpaca.getPositions();

      console.log(`Capital disponible: $${buyingPower}`);

      // Calcular capital por activo (dividir equitativamente)
      const capitalPerAsset = buyingPower * 0.8 / this.targetAssets.length; // Usar 80% del capital

      const allocation = {};
      for (const symbol of this.targetAssets) {
        const currentPosition = positions.find(p => p.symbol === symbol);
        const currentValue = currentPosition 
          ? parseFloat(currentPosition.market_value) 
          : 0;

        allocation[symbol] = {
          target: capitalPerAsset,
          current: currentValue,
          difference: capitalPerAsset - currentValue
        };
      }

      return allocation;
    } catch (error) {
      console.error('Error diversificando capital:', error);
      return {};
    }
  }

  async rebalancePortfolio() {
    try {
      const allocation = await this.diversifyCapital();
      
      for (const [symbol, data] of Object.entries(allocation)) {
        // Solo rebalancear si la diferencia es significativa (>10%)
        if (Math.abs(data.difference) > data.target * 0.1) {
          const currentPrice = await this.alpaca.getCryptoPrice(symbol);
          if (!currentPrice) continue;

          const qty = Math.abs(data.difference / currentPrice);
          
          if (data.difference > 0) {
            // Comprar más
            console.log(`Comprando ${qty.toFixed(8)} ${symbol}`);
            await this.alpaca.placeCryptoOrder(symbol, qty.toFixed(8), 'buy');
          } else {
            // Vender exceso
            console.log(`Vendiendo ${qty.toFixed(8)} ${symbol}`);
            await this.alpaca.placeCryptoOrder(symbol, qty.toFixed(8), 'sell');
          }
        }
      }
    } catch (error) {
      console.error('Error rebalanceando portafolio:', error);
    }
  }
}

module.exports = PortfolioManager;
