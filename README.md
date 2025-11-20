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
PyQt5==5.15.10
torch==2.9.1
transformers==4.44.2
datasets==3.1.0
accelerate==0.34.2
peft==0.18.0
psutil==5.9.8
fpdf2==2.8.1
matplotlib==3.9.2
pytest==7.4.3
pytest-qt==4.2.0
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
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Download or prepare model:**
   
   **Option A: Download from Hugging Face (Recommended)**
   ```bash
   pip install huggingface_hub
   python scripts/download_model.py
   ```
   
   **Option B: Manual download**
   ```bash
   Place your model files in the models/ directory
   Required files: config.json, tokenizer.json, model files (.safetensors or .bin)
   ```
   
   See [MODEL_STORAGE.md](MODEL_STORAGE.md) for detailed instructions on model storage and distribution.

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

Complete directory structure with detailed descriptions of all components:

```
LLS_M1/
│
├── 📂 desktop/
│   ├── __init__.py
│   ├── main.py
│   ├── TODO.txt
│   ├── IMPROVEMENTS.md
│   ├── NEXT_STEPS.md
│   │
│   ├── 📂 core/
│   │   ├── __init__.py
│   │   ├── model_manager.py
│   │   └── neural_network.py
│   │
│   ├── 📂 ui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── chat_widget.py
│   │   ├── styles.py
│   │   ├── theme_manager.py
│   │   │
│   │   ├── 📂 settings/
│   │   │   ├── __init__.py
│   │   │   └── settings_dialog.py
│   │   │
│   │   ├── 📂 history/
│   │   │   ├── __init__.py
│   │   │   ├── history_dialog.py
│   │   │   └── history_archive_dialog.py
│   │   │
│   │   ├── 📂 dashboard/
│   │   │   ├── __init__.py
│   │   │   ├── dashboard_widget.py
│   │   │   └── statistics_dialog.py
│   │   │
│   │   ├── 📂 monitoring/
│   │   │   ├── __init__.py
│   │   │   └── monitor_dialog.py
│   │   │
│   │   ├── 📂 plugins/
│   │   │   ├── __init__.py
│   │   │   └── plugin_dialog.py
│   │   │
│   │   ├── 📂 backup/
│   │   │   ├── __init__.py
│   │   │   └── backup_dialog.py
│   │   │
│   │   ├── 📂 user/
│   │   │   ├── __init__.py
│   │   │   ├── user_dialog.py
│   │   │   └── user_admin_dialog.py
│   │   │
│   │   ├── 📂 widgets/
│   │   │   ├── __init__.py
│   │   │   └── status_panel.py
│   │   │
│   │   └── 📂 images/
│   │       ├── actions.png
│   │       ├── backup.png
│   │       ├── clear.png
│   │       ├── history.png
│   │       ├── monitor.png
│   │       ├── quick_actions.png
│   │       ├── settings.png
│   │       └── theme.png
│   │
│   ├── 📂 config/
│   │   ├── __init__.py
│   │   └── settings.py
│   │
│   ├── 📂 utils/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── constants.py
│   │   ├── validators.py
│   │   ├── metrics.py
│   │   ├── draft_manager.py
│   │   ├── chat_history.py
│   │   └── model_downloader.py
│   │
│   ├── 📂 plugins/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── manager.py
│   │   └── 📂 examples/
│   │       ├── __init__.py
│   │       ├── web_search.py
│   │       └── knowledge_base.py
│   │
│   ├── 📂 history/
│   │   ├── __init__.py
│   │   ├── manager.py
│   │   └── exporters.py
│   │
│   ├── 📂 monitoring/
│   │   ├── __init__.py
│   │   └── system_monitor.py
│   │
│   ├── 📂 training/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── pipeline.py
│   │   ├── trainer.py
│   │   ├── dataset.py
│   │   │
│   │   │
│   │   ├── evaluation.py
│   │   │
│   │   │
│   │   ├── status.py
│   │   ├── utils.py
│   │   │
│   │   ├── 📂 configs/
│   │   │   └── example.json
│   │   │
│   │   ├── 📂 scripts/
│   │   │   ├── __init__.py
│   │   │   ├── run_finetune.py
│   │   │   └── plot_reports.py
│   │   │
│   │   └── 📂 reports/
│   │       ├── __init__.py
│   │       ├── report_builder.py
│   │       └── plotter.py
│   │
│   ├── 📂 database/
│   │   ├── __init__.py
│   │   ├── db.py
│   │   │
│   │   │
│   │   ├── 📂 models/
│   │   │   └── user.py
│   │   │
│   │   └── 📂 repositories/
│   │       ├── __init__.py
│   │       └── user_repository.py
│   │
│   │
│   │
│   ├── 📂 backup/
│   │   ├── __init__.py
│   │   └── backup_manager.py
│   │
│   │
│   │
│   │
│   ├── 📂 updater/
│   │   ├── __init__.py
│   │   └── update_manager.py
│   │
│   │
│   │
│   │
│   ├── 📂 shortcuts/
│   │   ├── __init__.py
│   │   ├── actions.py
│   │   │
│   │   │
│   │   └── quick_actions_dialog.py
│   │
│   ├── 📂 appearance/
│   │   ├── __init__.py
│   │   └── palette_manager.py
│   │
│   └── 📂 knowledge/
│       ├── __init__.py
│       └── articles.json
│
├── 📂 models/
│   ├── config.json
│   ├── tokenizer.json
│   ├── tokenizer_config.json
│   ├── special_tokens_map.json
│   ├── generation_config.json
│   ├── model.safetensors.index.json
│   ├── model-*.safetensors
│   ├── modelling_deepseek.py
│   ├── configuration_deepseek.py
│   ├── gitattributes
│   └── MISSING_FILES.txt
│
├── 📂 data/
│   ├── chat_history.json
│   ├── 📂 backups/
│   │   └── (backup files created here)
│   ├── 📂 exports/
│   │   └── (JSON/Markdown/PDF exports)
│   ├── 📂 archives/
│   │   └── (compressed archives)
│   ├── 📂 database/
│   │   └── app.db
│   └── 📂 updater/
│       └── model_hashes.json
│
├── 📂 config/
│   ├── config.json
│   └── config.json.backup
│
├── 📂 logs/
│   ├── app.log
│   ├── errors.log
│   └── metrics.log
│
├── 📂 tests/
│   ├── __init__.py
│   ├── test_settings.py
│   └── test_validators.py
│
├── 📂 .github/
│   └── 📂 workflows/
│       └── tests.yml
│
├── 📄 requirements.txt
├── 📄 .editorconfig
├── 📄 .gitignore
├── 📄 README.md
└── 📄 LICENSE
```

### Directory Descriptions

#### 🎯 Core Directories

- **`desktop/`** - Main application code, organized by functionality
- **`models/`** - Language model files (weights, configs, tokenizers)
- **`data/`** - Runtime data (history, backups, exports, database)
- **`config/`** - Configuration files and backups
- **`logs/`** - Application and error logs
- **`tests/`** - Unit and integration tests

#### 📦 Key Modules

1. **Core (`desktop/core/`)** - Model loading and inference
2. **UI (`desktop/ui/`)** - All user interface components
3. **Utils (`desktop/utils/`)** - Shared utilities and helpers
4. **Plugins (`desktop/plugins/`)** - Extensible plugin system
5. **Training (`desktop/training/`)** - Model fine-tuning pipeline
6. **Database (`desktop/database/`)** - Data persistence layer

#### 🔧 Configuration Files

- **`config/config.json`** - Main application configuration
- **`requirements.txt`** - Python package dependencies
- **`.editorconfig`** - Code formatting standards
- **`.gitignore`** - Version control exclusions

#### 📊 Data Files

- **`data/chat_history.json`** - Conversation history
- **`data/database/app.db`** - SQLite user database
- **`logs/app.log`** - Application activity log
- **`logs/errors.log`** - Error tracking log

---

## 📚 API Documentation

### Core Classes

#### `NeuralNetwork`

Main interface for interacting with language models.

```python
from desktop.core.neural_network import NeuralNetwork
from desktop.config.settings import Settings

settings = Settings()
nn = NeuralNetwork(settings=settings)
response = nn.generate_response("Hello, how are you?")
nn.update_generation_params({"temperature": 0.7})
nn.reload_model()
```

#### `Settings`

Configuration management.

```python
from desktop.config.settings import Settings

settings = Settings()
theme = settings.get_theme()
settings.set_theme("dark")
gen_config = settings.get_generation_config()
settings.update_generation_config({"temperature": 0.8})
```

#### `MetricsCollector`

Performance metrics tracking.

```python
from desktop.utils.metrics import get_metrics_collector

metrics = get_metrics_collector()
metrics.record_response(response_time=2.5, success=True)
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
   source venv/bin/activate
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
pytest
pytest --cov=desktop --cov-report=html
pytest tests/test_settings.py
pytest -v
```

### Code Quality Tools

```bash
black desktop/ tests/
flake8 desktop/ tests/
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
pytest
pytest tests/test_settings.py
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
