# 📦 Руководство по хранению и распространению моделей

## 🎯 Рекомендуемые решения для бесплатного хранения моделей

### 1. Hugging Face Hub (⭐ Рекомендуется)

**Почему Hugging Face:**
- ✅ Полностью бесплатно для публичных моделей
- ✅ Неограниченное хранилище
- ✅ CDN для быстрой загрузки
- ✅ Интеграция с transformers (автоматическая загрузка)
- ✅ Версионирование моделей
- ✅ API для программной загрузки
- ✅ Поддержка больших файлов (sharded models)

**Как использовать:**

#### Шаг 1: Создайте аккаунт на Hugging Face
1. Перейдите на https://huggingface.co
2. Зарегистрируйтесь (бесплатно)
3. Создайте новый репозиторий для модели

#### Шаг 2: Загрузите модель
```bash
pip install huggingface_hub
huggingface-cli login
huggingface-cli upload your-username/your-model-name ./models/
```

#### Шаг 3: Используйте в приложении
```python
from desktop.utils.model_downloader import ModelDownloader

downloader = ModelDownloader()
result = downloader.download_from_huggingface('your-username/your-model-name')

if result['success']:
    model_path = result['path']
```

**Пример конфигурации:**
```json
{
  "model_source": {
    "type": "huggingface",
    "repo_id": "your-username/your-model-name",
    "revision": "main"
  }
}
```

---

### 2. Git LFS (для небольших моделей)

**Ограничения:**
- GitHub: 1GB бесплатно, затем $5/месяц за 50GB
- GitLab: 10GB бесплатно
- Bitbucket: 1GB бесплатно

**Как использовать:**

```bash
git lfs install
git lfs track "*.safetensors"
git lfs track "*.bin"
git add .gitattributes
git add models/
git commit -m "Add model files"
git push
```

**⚠️ Важно:** Git LFS не подходит для очень больших моделей (>1GB), так как есть лимиты.

---

### 3. GitHub Releases

**Ограничения:**
- 2GB на файл
- Неограниченное хранилище для релизов

**Как использовать:**

1. Создайте релиз на GitHub
2. Прикрепите модель как asset
3. Используйте прямую ссылку для загрузки

```python
# Пример загрузки из GitHub Releases
url = "https://github.com/username/repo/releases/download/v1.0/model.zip"
downloader.download_from_url(url)
```

---

### 4. Альтернативные решения

#### Google Drive / OneDrive
- ✅ Бесплатно (15GB Google, 5GB OneDrive)
- ❌ Неудобно для автоматизации
- ❌ Медленная загрузка
- ❌ Нужны прямые ссылки

#### IPFS (InterPlanetary File System)
- ✅ Децентрализованное хранилище
- ✅ Бесплатно
- ❌ Требует настройки
- ❌ Медленная загрузка без пиров

#### Модель на вашем сервере
- ✅ Полный контроль
- ❌ Требует сервер и трафик
- ❌ Плата за хостинг

---

## 🚀 Интеграция в приложение

### Автоматическая загрузка при первом запуске

Добавьте в `desktop/main.py` или `desktop/ui/main_window.py`:

```python
from desktop.utils.model_downloader import ModelDownloader
from desktop.config.settings import Settings

def check_and_download_model():
    settings = Settings()
    model_path = settings.get_model_path()
    
    downloader = ModelDownloader()
    
    # Проверяем наличие модели
    if not downloader.check_model_exists(model_path):
        print("Модель не найдена. Начинаем загрузку...")
        
        # Загружаем из Hugging Face
        result = downloader.download_from_huggingface(
            repo_id='your-username/your-model-name'
        )
        
        if result['success']:
            # Обновляем путь в настройках
            settings.set_model_path(result['path'])
            print(f"Модель загружена: {result['path']}")
        else:
            print(f"Ошибка загрузки: {result['error']}")
```

### UI для загрузки модели

Создайте диалог загрузки модели:

```python
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
from desktop.utils.model_downloader import ModelDownloader

class ModelDownloadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.downloader = ModelDownloader()
        self.setup_ui()
    
    def download_model(self, repo_id: str):
        self.progress_bar.setValue(0)
        
        def update_progress(value):
            self.progress_bar.setValue(int(value * 100))
        
        result = self.downloader.download_from_huggingface(
            repo_id=repo_id,
            progress_callback=update_progress
        )
        
        if result['success']:
            self.accept()
        else:
            # Показать ошибку
            pass
```

---

## 📋 Чек-лист для публикации модели

- [ ] Создан аккаунт на Hugging Face
- [ ] Создан репозиторий для модели
- [ ] Модель загружена в репозиторий
- [ ] Добавлено README с описанием модели
- [ ] Указаны требования (память, GPU и т.д.)
- [ ] Добавлены примеры использования
- [ ] Обновлена документация приложения
- [ ] Протестирована загрузка модели

---

## 🔧 Скрипт для загрузки модели

Создайте `scripts/download_model.py`:

```python
#!/usr/bin/env python3
"""Скрипт для загрузки модели из Hugging Face."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from desktop.utils.model_downloader import download_model_interactive

if __name__ == '__main__':
    model_path = download_model_interactive()
    if model_path:
        print(f"\nМодель готова к использованию: {model_path}")
        print("Обновите путь в настройках приложения.")
    else:
        print("\nЗагрузка отменена или завершилась с ошибкой.")
```

Использование:
```bash
python scripts/download_model.py
```

---

## 💡 Рекомендации

1. **Используйте Hugging Face Hub** - это лучший вариант для ML моделей
2. **Разбивайте большие модели** на части (sharding) - уже поддерживается
3. **Добавьте инструкции** в README о том, как скачать модель
4. **Предоставьте несколько вариантов** - Hugging Face + резервные ссылки
5. **Автоматизируйте загрузку** - добавьте проверку при первом запуске

---

## 📚 Полезные ссылки

- [Hugging Face Hub Documentation](https://huggingface.co/docs/hub)
- [Hugging Face Upload Guide](https://huggingface.co/docs/hub/uploading)
- [Git LFS Documentation](https://git-lfs.github.com/)
- [GitHub Releases API](https://docs.github.com/en/rest/releases)

---

## ❓ FAQ

**Q: Модель весит 10GB, что делать?**  
A: Используйте Hugging Face Hub - нет лимитов на размер для публичных моделей.

**Q: Как сделать модель приватной?**  
A: На Hugging Face можно сделать репозиторий приватным (требует подписку Pro).

**Q: Можно ли использовать несколько источников?**  
A: Да, можно добавить fallback механизм - сначала Hugging Face, потом резервные ссылки.

**Q: Как ускорить загрузку?**  
A: Используйте резюме загрузки (resume_download=True) и параллельную загрузку shards.

