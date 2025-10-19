const MLModel = require('../src/ml-model');

module.exports = async (req, res) => {
  try {
    console.log('🔄 Refrescando modelos desde Google Drive...');
    
    const mlModel = new MLModel();
    await mlModel.downloadModelsFromDrive();
    
    const info = mlModel.getModelInfo();
    
    res.status(200).json({
      success: true,
      message: 'Modelos actualizados correctamente',
      info: info,
      timestamp: new Date().toISOString()
