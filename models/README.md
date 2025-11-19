# Models Directory

This directory stores neural network models used by the application.

## Structure

Place your model files or directories here. The application will look for models in this directory.

## Supported Formats

- Hugging Face models (local directories)
- Model files compatible with transformers library

## Usage

1. Download or place your model files in this directory
2. Configure the model path in the application settings
3. The model path should point to either:
   - A directory containing model files (e.g., `models/my-model/`)
   - A specific model file if applicable

## Example

```
models/
  ├── my-model/
  │   ├── config.json
  │   ├── pytorch_model.bin
  │   ├── tokenizer_config.json
  │   └── vocab.json
  └── README.md
```

## Notes

- Models are loaded using the `transformers` library
- The default model path is set to this directory
- You can change the model path in the application settings

