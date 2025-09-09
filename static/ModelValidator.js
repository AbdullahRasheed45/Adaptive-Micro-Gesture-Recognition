// TFLite Model Validation Utility
import * as tf from "@tensorflow/tfjs"

class ModelValidator {
  constructor() {
    this.expectedInputShape = [1, 4, 21, 3]
    this.expectedOutputClasses = 12
  }

  async validateModel(model) {
    try {
      console.log("Validating TFLite model...")

      // Check if model has the expected structure
      if (!model.inputs || !model.outputs) {
        throw new Error("Model doesn't have proper input/output structure")
      }

      // Validate input shape
      const inputShape = model.inputs[0].shape
      console.log("Model input shape:", inputShape)

      if (!this.compareShapes(inputShape, this.expectedInputShape)) {
        console.warn(`Input shape mismatch. Expected: ${this.expectedInputShape}, Got: ${inputShape}`)
      }

      // Validate output shape
      const outputShape = model.outputs[0].shape
      console.log("Model output shape:", outputShape)

      if (outputShape[outputShape.length - 1] !== this.expectedOutputClasses) {
        console.warn(
          `Output classes mismatch. Expected: ${this.expectedOutputClasses}, Got: ${outputShape[outputShape.length - 1]}`,
        )
      }

      // Test with dummy data
      await this.testModelInference(model)

      console.log("✅ Model validation successful")
      return true
    } catch (error) {
      console.error("❌ Model validation failed:", error)
      return false
    }
  }

  compareShapes(shape1, shape2) {
    if (shape1.length !== shape2.length) return false

    for (let i = 0; i < shape1.length; i++) {
      // Allow -1 or null for dynamic dimensions
      if (shape1[i] !== shape2[i] && shape1[i] !== -1 && shape1[i] !== null) {
        return false
      }
    }
    return true
  }

  async testModelInference(model) {
    console.log("Testing model inference with dummy data...")

    // Create dummy input tensor [1, 4, 21, 3]
    const dummyData = new Array(1 * 4 * 21 * 3).fill(0).map(() => Math.random())
    const dummyTensor = tf.tensor4d(dummyData, [1, 4, 21, 3])

    try {
      const prediction = model.predict(dummyTensor)
      const result = prediction.dataSync ? prediction.dataSync() : await prediction.data()

      console.log("Test prediction shape:", result.length)
      console.log("Test prediction sample:", Array.from(result).slice(0, 5))

      // Clean up
      dummyTensor.dispose()
      if (prediction.dispose) prediction.dispose()

      return true
    } catch (error) {
      dummyTensor.dispose()
      throw error
    }
  }

  async checkModelFile() {
    try {
      const response = await fetch("/api/model-info")
      const info = await response.json()

      if (!info.model_available) {
        throw new Error(info.message || "Model file not available")
      }

      console.log("Model file info:", info)
      return info
    } catch (error) {
      console.error("Error checking model file:", error)
      throw error
    }
  }
}

export { ModelValidator }
