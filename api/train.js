const MLModel = require('../src/ml-model');

module.exports = async (req, res) => {
  try {
    const mlModel = new MLModel();
    await mlModel.downloadModelsFromDrive();
    
    res.status(200).json({
      success: true,
      message: 'Modelos actualizados desde Google Drive',
      models: Object.keys(mlModel.models),
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
};
