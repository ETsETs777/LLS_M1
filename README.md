# 🚀 LLS_M1 - Desktop Application for Language Models

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15.10-green.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.9.1-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

**Professional desktop application for interacting with Large Language Models (LLMs)**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Screenshots](#-screenshots)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## 🎯 Overview

**LLS_M1** is a feature-rich desktop application built with PyQt5 for seamless interaction with Large Language Models. It provides an intuitive interface for chatting with AI models, managing conversations, monitoring system resources, and extending functionality through plugins.

### Key Highlights

- 🎨 **Modern UI** - Clean, responsive interface with light/dark themes
- ⚡ **High Performance** - Optimized for both CPU and GPU inference
- 🔌 **Extensible** - Plugin system for custom functionality
- 📊 **Analytics** - Built-in metrics and monitoring
- 🔒 **Secure** - Input validation and secure data handling
- 🛠️ **Developer-Friendly** - Well-documented codebase with type hints

---

## ✨ Features

### Core Functionality

#### 💬 **Chat Interface**
- Intuitive chat interface with real-time message display
- Rich text formatting with HTML support
- Message timestamps and user/bot distinction
- Auto-scroll to latest messages
- Loading indicators during generation

#### 🎨 **Theming & Appearance**
- Light and dark themes
- Customizable accent colors
- Smooth theme transitions
- High DPI display support

#### 📚 **History Management**
- Automatic conversation history saving
- Search functionality with keyword filtering
- Tag-based message organization
- Export to JSON, Markdown, and PDF formats
- Automatic cleanup of old records
- Archive system for long-term storage

#### 🏷️ **Tagging System**
- Add multiple tags to messages
- Filter conversations by tags
- Tag-based statistics and analytics
- Quick tag management

#### 📊 **Resource Monitoring**
- Real-time CPU/GPU/RAM usage tracking
- GPU memory monitoring with warnings
- Response time metrics
- Historical metrics logging
- Visual resource usage display

#### 🔌 **Plugin System**
- Extensible plugin architecture
- Role-based plugin access control
- Built-in plugins (Web Search, Knowledge Base)
- Easy plugin development API
- Plugin enable/disable management

#### 💾 **Backup & Recovery**
- Automatic backup creation
- Manual backup scheduling
- Backup restoration
- Data integrity verification

#### 👥 **User Management**
- Multi-user support
- Role-based access control (Admin, Analyst, User)
- User profile management
- Session management

#### 🎯 **Quick Actions**
- Keyboard shortcuts for common operations
- Customizable quick actions
- Command palette
- Batch operations

#### 📈 **Statistics & Analytics**
- Conversation statistics
- Message count and session tracking
- Plugin usage analytics
- Training status monitoring
- Performance metrics

#### 🧠 **Model Management**
- Model validation on startup
- Model reloading without restart
- Device selection (CPU/GPU)
- Generation parameter tuning
- Model metadata display

#### 🎓 **Training Pipeline**
- Fine-tuning support
- Multiple dataset support
- Training progress monitoring
- Loss/accuracy visualization
- Training reports generation

### Advanced Features

- **Auto-save Drafts** - Unfinished messages are automatically saved
- **Metrics Collection** - Response time tracking and success rate monitoring
- **Error Handling** - Comprehensive error handling with recovery
- **Logging System** - Centralized logging with file rotation
- **Input Validation** - Message length and content validation
- **Resource Cleanup** - Proper cleanup of threads and GPU memory
- **Configuration Management** - Batched saves and caching
- **Type Safety** - Full type hints throughout codebase

---

## 📸 Screenshots

> **Note:** Screenshots would be added here showing:
> - Main chat interface
> - Settings dialog
> - History management
> - Resource monitoring
> - Plugin management

---

## 📦 Requirements

### System Requirements

- **OS**: Windows 10+, Linux, macOS
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB+ recommended)
- **Storage**: 2GB+ free space
- **GPU**: Optional (CUDA-compatible GPU recommended for better performance)

### Python Dependencies

All dependencies are listed in `requirements.txt`:

```
PyQt5==5.15.10          # GUI framework
torch==2.9.1            # Deep learning framework
transformers==4.44.2    # Hugging Face transformers
datasets==3.1.0         # Dataset handling
accelerate==0.34.2      # Model acceleration
peft==0.18.0            # Parameter-efficient fine-tuning
psutil==5.9.8           # System monitoring
fpdf2==2.8.1            # PDF generation
matplotlib==3.9.2       # Plotting and visualization
pytest==7.4.3           # Testing framework
pytest-qt==4.2.0        # PyQt testing support
```

### Optional Dependencies

- **CUDA Toolkit** (for GPU acceleration)
- **Git** (for version control)

---

## 🚀 Installation

### Method 1: From Source (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ETsETs777/LLS_M1.git
   cd LLS_M1
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Prepare model directory:**
   ```bash
   # Place your model files in the models/ directory
   # Required files:
   # - config.json
   # - tokenizer.json
   # - model files (.safetensors or .bin)
   ```

### Method 2: Using pip (if available)

```bash
pip install lls-m1
```

### Method 3: Docker (Coming Soon)

```bash
docker pull etsets777/lls-m1:latest
docker run -it etsets777/lls-m1
```

---

## ⚡ Quick Start

1. **Start the application:**
   ```bash
   python desktop/main.py
   ```

2. **First-time setup:**
   - The application will create default configuration files
   - Set your model path in Settings (Ctrl+,)
   - Configure generation parameters if needed

3. **Start chatting:**
   - Type your message in the input field
   - Press Enter or click "Отправить"
   - Wait for the model to generate a response

---

## 📖 Usage

### Basic Operations

#### Starting a Conversation

1. Open the application
2. Type your message in the input field at the bottom
3. Press `Enter` or click the "Отправить" button
4. The model will generate a response (shown with green text)

#### Managing History

- **View History**: Click the history icon or press `Ctrl+H`
- **Search**: Use the search box in the history dialog
- **Export**: Right-click on conversations to export
- **Archive**: Use the archive feature for long-term storage

#### Using Tags

1. Click the "Теги" button
2. Enter tags separated by commas (e.g., `work, important, todo`)
3. Tags will be saved with your message
4. Filter conversations by tags in the history dialog

#### Changing Themes

- Click the theme icon in the chat interface
- Or use menu: `Вид` → `Светлая тема` / `Темная тема`
- Or use shortcut: Defined in quick actions

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+,` | Open Settings |
| `Ctrl+H` | Open History |
| `Ctrl+L` | Clear Chat |
| `Ctrl+Q` | Quit Application |
| `Ctrl+R` | Reload Model |
| `F5` | Refresh Metrics |
| `Enter` | Send Message |

### Advanced Usage

#### Customizing Generation Parameters

1. Open Settings (`Ctrl+,`)
2. Navigate to "Generation" section
3. Adjust:
   - **Temperature**: Controls randomness (0.0-2.0)
   - **Top-p**: Nucleus sampling threshold (0.0-1.0)
   - **Max Tokens**: Maximum response length
   - **Repetition Penalty**: Reduces repetition

#### Creating Presets

1. Configure your desired settings
2. Go to Settings → Presets
3. Click "Save Preset"
4. Name your preset
5. Switch between presets quickly

#### Using Plugins

1. Open Plugins dialog (Tools → Plugins)
2. Enable desired plugins
3. Plugins will be available in the chat interface
4. Configure plugin settings if needed

#### Monitoring Resources

1. Open Resource Monitor (Tools → Мониторинг ресурсов)
2. View real-time CPU/GPU/RAM usage
3. Check GPU memory warnings
4. View historical metrics in logs

---

## ⚙️ Configuration

### Configuration File Location

- **Windows**: `%APPDATA%\LLS_M1\config\config.json`
- **Linux**: `~/.config/LLS_M1/config.json`
- **macOS**: `~/Library/Application Support/LLS_M1/config/config.json`

### Configuration Structure

```json
{
  "model_path": "path/to/model",
  "theme": "light",
  "prompt": "System prompt text",
  "generation": {
    "max_new_tokens": 200,
    "temperature": 0.8,
    "top_p": 0.95,
    "do_sample": true,
    "repetition_penalty": 1.05
  },
  "history": {
    "retention_days": 90,
    "export_dir": "data/exports"
  },
  "plugins": {
    "enabled": ["knowledge_base"],
    "available": { ... }
  }
}
```

### Environment Variables

- `LLS_M1_MODEL_PATH`: Override default model path
- `LLS_M1_LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `LLS_M1_CONFIG_DIR`: Custom configuration directory

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────┐
│           Main Window (UI)              │
├─────────────────────────────────────────┤
│  Chat Widget  │  Settings  │  History   │
├─────────────────────────────────────────┤
│         Neural Network Layer            │
├─────────────────────────────────────────┤
│         Model Manager                   │
├─────────────────────────────────────────┤
│    Transformers / PyTorch               │
└─────────────────────────────────────────┘
```

### Component Overview

- **UI Layer**: PyQt5 widgets and dialogs
- **Business Logic**: Core application logic
- **Model Layer**: Model loading and inference
- **Data Layer**: Configuration and history management
- **Plugin System**: Extensible plugin architecture

### Design Patterns

- **Singleton**: Logger, Metrics Collector
- **Factory**: Plugin creation
- **Observer**: Event handling
- **Strategy**: Generation parameters
- **Repository**: Data access

---

## 📁 Project Structure

```
LLS_M1/
├── desktop/                    # Main application code
│   ├── core/                   # Core functionality
│   │   ├── model_manager.py    # Model loading and management
│   │   └── neural_network.py   # Neural network wrapper
│   ├── ui/                      # User interface
│   │   ├── main_window.py      # Main application window
│   │   ├── chat_widget.py      # Chat interface
│   │   ├── settings/           # Settings dialogs
│   │   ├── history/            # History management UI
│   │   ├── plugins/            # Plugin management UI
│   │   └── styles.py           # UI styles
│   ├── config/                  # Configuration
│   │   └── settings.py         # Settings management
│   ├── utils/                   # Utilities
│   │   ├── logger.py           # Logging system
│   │   ├── metrics.py          # Performance metrics
│   │   ├── validators.py       # Input validation
│   │   ├── constants.py        # Application constants
│   │   └── draft_manager.py    # Draft management
│   ├── plugins/                 # Plugin system
│   │   ├── base.py             # Base plugin class
│   │   ├── manager.py          # Plugin manager
│   │   └── examples/           # Example plugins
│   ├── history/                 # History management
│   │   ├── manager.py          # History manager
│   │   └── exporters.py        # Export functionality
│   ├── monitoring/              # System monitoring
│   │   └── system_monitor.py   # Resource monitoring
│   ├── training/                # Training pipeline
│   │   ├── pipeline.py         # Training pipeline
│   │   ├── trainer.py          # Model trainer
│   │   └── evaluation.py      # Model evaluation
│   └── main.py                 # Application entry point
├── models/                      # Model files directory
├── data/                        # Application data
│   ├── backups/                # Backup files
│   ├── exports/                # Exported conversations
│   ├── archives/               # Archived history
│   └── database/               # Database files
├── config/                      # Configuration files
├── logs/                        # Log files
├── tests/                       # Test suite
│   ├── test_settings.py
│   └── test_validators.py
├── .github/                     # GitHub workflows
│   └── workflows/
│       └── tests.yml
├── requirements.txt             # Python dependencies
├── .editorconfig               # Editor configuration
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
└── LICENSE                     # License file
```

---

## 📚 API Documentation

### Core Classes

#### `NeuralNetwork`

Main interface for interacting with language models.

```python
from desktop.core.neural_network import NeuralNetwork
from desktop.config.settings import Settings

# Initialize
settings = Settings()
nn = NeuralNetwork(settings=settings)

# Generate response
response = nn.generate_response("Hello, how are you?")

# Update parameters
nn.update_generation_params({"temperature": 0.7})

# Reload model
nn.reload_model()
```

#### `Settings`

Configuration management.

```python
from desktop.config.settings import Settings

settings = Settings()

# Get/Set values
theme = settings.get_theme()
settings.set_theme("dark")

# Generation config
gen_config = settings.get_generation_config()
settings.update_generation_config({"temperature": 0.8})
```

#### `MetricsCollector`

Performance metrics tracking.

```python
from desktop.utils.metrics import get_metrics_collector

metrics = get_metrics_collector()

# Record a response
metrics.record_response(response_time=2.5, success=True)

# Get statistics
stats = metrics.get_stats()
print(f"Average response time: {stats['avg_response_time']}s")
print(f"Success rate: {stats['success_rate']}%")
```

### Plugin Development

Create custom plugins by extending the base `Plugin` class:

```python
from desktop.plugins.base import Plugin

class MyCustomPlugin(Plugin):
    name = "My Plugin"
    description = "Description of my plugin"
    
    def execute(self, input_text: str) -> str:
        # Your plugin logic here
        return f"Processed: {input_text}"
```

---

## 🛠️ Development

### Setting Up Development Environment

1. **Clone and setup:**
   ```bash
   git clone https://github.com/ETsETs777/LLS_M1.git
   cd LLS_M1
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Install development dependencies:**
   ```bash
   pip install pytest pytest-qt black flake8 mypy
   ```

3. **Run in development mode:**
   ```bash
   python desktop/main.py
   ```

### Code Style

The project follows PEP 8 with some modifications:

- **Line length**: 120 characters
- **Indentation**: 4 spaces
- **Type hints**: Required for all functions
- **Docstrings**: Google style

Use `.editorconfig` for consistent formatting.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=desktop --cov-report=html

# Run specific test file
pytest tests/test_settings.py

# Run with verbose output
pytest -v
```

### Code Quality Tools

```bash
# Format code
black desktop/ tests/

# Lint code
flake8 desktop/ tests/

# Type checking
mypy desktop/
```

---

## 🧪 Testing

### Test Coverage

The project includes unit tests for:
- Configuration management
- Input validation
- Model management (planned)
- Plugin system (planned)

### Running Tests

```bash
# All tests
pytest

# Specific module
pytest tests/test_settings.py

# With coverage report
pytest --cov=desktop --cov-report=term-missing
```

### Writing Tests

Example test structure:

```python
import pytest
from desktop.config.settings import Settings

def test_settings_creation():
    settings = Settings()
    assert settings is not None
    assert settings.get_theme() in ['light', 'dark']
```

---

## 🔧 Troubleshooting

### Common Issues

#### Model Not Loading

**Problem**: Model fails to load on startup

**Solutions**:
1. Check model path in settings
2. Verify all required files are present:
   - `config.json`
   - `tokenizer.json`
   - Model weights (`.safetensors` or `.bin`)
3. Check logs in `logs/app.log`
4. Verify CUDA/GPU availability if using GPU

#### Out of Memory Errors

**Problem**: GPU out of memory during generation

**Solutions**:
1. Reduce `max_new_tokens` in generation settings
2. Use CPU instead of GPU
3. Close other GPU-intensive applications
4. Reload the model to clear memory

#### Slow Response Times

**Problem**: Model responses are slow

**Solutions**:
1. Use GPU if available
2. Reduce `max_new_tokens`
3. Check system resource usage
4. Verify model is loaded on correct device

#### Configuration Errors

**Problem**: Configuration file is corrupted

**Solutions**:
1. Check for backup in `config/config.json.backup`
2. Delete corrupted config (will recreate defaults)
3. Check logs for specific error messages

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/ETsETs777/LLS_M1/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ETsETs777/LLS_M1/discussions)
- **Logs**: Check `logs/app.log` and `logs/errors.log`

---

## 🗺️ Roadmap

### Short Term (v1.1)
- [ ] Progress bars for long operations
- [ ] Retry mechanism for errors
- [ ] Enhanced exception handling
- [ ] User tutorials and tooltips

### Medium Term (v1.2)
- [ ] Undo/Redo functionality
- [ ] Enhanced search with filters
- [ ] Data encryption for sensitive config
- [ ] Real-time metrics graphs

### Long Term (v2.0)
- [ ] Multi-language support (i18n)
- [ ] Docker containerization
- [ ] Web interface option
- [ ] Model marketplace integration
- [ ] Advanced analytics dashboard

See [NEXT_STEPS.md](desktop/NEXT_STEPS.md) for detailed roadmap.

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Write/update tests**
5. **Ensure all tests pass:**
   ```bash
   pytest
   ```
6. **Commit your changes:**
   ```bash
   git commit -m "Add amazing feature"
   ```
7. **Push to your fork:**
   ```bash
   git push origin feature/amazing-feature
   ```
8. **Open a Pull Request**

### Contribution Guidelines

- Follow the existing code style
- Add tests for new features
- Update documentation as needed
- Write clear commit messages
- Keep PRs focused and small

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **PyQt5** - GUI framework
- **Hugging Face** - Transformers library
- **PyTorch** - Deep learning framework
- **All Contributors** - Thanks to everyone who contributed!

---

## 📞 Contact & Support

- **Author**: ETsETs777
- **Repository**: [https://github.com/ETsETs777/LLS_M1](https://github.com/ETsETs777/LLS_M1)
- **Issues**: [GitHub Issues](https://github.com/ETsETs777/LLS_M1/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ETsETs777/LLS_M1/discussions)

---

<div align="center">

**Made with ❤️ by ETsETs777**

⭐ Star this repo if you find it useful!

[⬆ Back to Top](#-lls_m1---desktop-application-for-language-models)

</div>
