const TradingStrategy = require('../src/strategy');

module.exports = async (req, res) => {
  try {
    const strategy = new TradingStrategy();
    await strategy.initialize();
    
    const status = await strategy.getStatus();
    
    res.status(200).json({
      success: true,
      status: status,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
};
