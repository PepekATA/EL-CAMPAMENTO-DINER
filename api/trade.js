const TradingStrategy = require('../src/strategy');

let strategy = null;

module.exports = async (req, res) => {
  try {
    // Inicializar estrategia si no existe
    if (!strategy) {
      strategy = new TradingStrategy();
      await strategy.initialize();
    }

    // Ejecutar estrategia de trading
    await strategy.executeScalpingStrategy();

    const status = await strategy.getStatus();
    
    res.status(200).json({
      success: true,
      message: 'Trading ejecutado correctamente',
      timestamp: new Date().toISOString(),
      status: status
    });

  } catch (error) {
    console.error('Error en endpoint de trading:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
};
