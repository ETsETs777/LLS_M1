import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from urllib.parse import urlparse

from desktop.utils.logger import get_logger

logger = get_logger('desktop.utils.model_downloader')

try:
    from huggingface_hub import snapshot_download, hf_hub_download
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    logger.warning("huggingface_hub не установлен. Установите: pip install huggingface_hub")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests не установлен. Установите: pip install requests")


class ModelDownloader:
    def __init__(self, download_dir: Optional[str] = None):
        if download_dir is None:
            base_dir = Path(__file__).parent.parent.parent
            download_dir = base_dir / 'models'
        
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    def download_from_huggingface(
        self,
        repo_id: str,
        revision: Optional[str] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Dict[str, Any]:
        if not HUGGINGFACE_AVAILABLE:
            return {
                'success': False,
                'error': 'huggingface_hub не установлен. Установите: pip install huggingface_hub'
            }
        
        try:
            logger.info(f"Начало загрузки модели из Hugging Face: {repo_id}")
            local_dir = self.download_dir / repo_id.split('/')[-1]
            snapshot_download(
                repo_id=repo_id,
                revision=revision,
                local_dir=str(local_dir),
                local_dir_use_symlinks=False,
                resume_download=True
            )
            
            logger.info(f"Модель успешно загружена в: {local_dir}")
            
            return {
                'success': True,
                'path': str(local_dir),
                'repo_id': repo_id,
                'revision': revision or 'main'
            }
        except Exception as e:
            logger.exception(f"Ошибка при загрузке модели из Hugging Face: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def download_from_url(
        self,
        url: str,
        filename: Optional[str] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Dict[str, Any]:
        if not REQUESTS_AVAILABLE:
            return {
                'success': False,
                'error': 'requests не установлен. Установите: pip install requests'
            }
        
        try:
            logger.info(f"Начало загрузки файла: {url}")
            
            if filename is None:
                filename = os.path.basename(urlparse(url).path) or 'downloaded_file'
            
            filepath = self.download_dir / filename
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = downloaded / total_size
                            progress_callback(progress)
            
            logger.info(f"Файл успешно загружен: {filepath}")
            
            return {
                'success': True,
                'path': str(filepath),
                'size': downloaded
            }
        except Exception as e:
            logger.exception(f"Ошибка при загрузке файла: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def download_model_files(
        self,
        source: str,
        source_type: str = 'auto',
        **kwargs
    ) -> Dict[str, Any]:
        if source_type == 'auto':
            if source.startswith('http://') or source.startswith('https://'):
                source_type = 'url'
            elif '/' in source and not os.path.exists(source):
                source_type = 'huggingface'
            else:
                source_type = 'local'
        
        if source_type == 'huggingface':
            return self.download_from_huggingface(
                repo_id=source,
                revision=kwargs.get('revision'),
                progress_callback=kwargs.get('progress_callback')
            )
        elif source_type == 'url':
            return self.download_from_url(
                url=source,
                filename=kwargs.get('filename'),
                progress_callback=kwargs.get('progress_callback')
            )
        elif source_type == 'local':
            source_path = Path(source)
            if not source_path.exists():
                return {
                    'success': False,
                    'error': f'Локальный путь не существует: {source}'
                }
            
            dest_path = self.download_dir / source_path.name
            if source_path.is_dir():
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
            else:
                shutil.copy2(source_path, dest_path)
            
            return {
                'success': True,
                'path': str(dest_path)
            }
        else:
            return {
                'success': False,
                'error': f'Неизвестный тип источника: {source_type}'
            }
    
    def check_model_exists(self, model_path: str) -> bool:
        path = Path(model_path)
        if not path.exists():
            return False
        required_files = ['config.json', 'tokenizer.json']
        for file in required_files:
            if not (path / file).exists():
                return False
        
        return True


def download_model_interactive() -> Optional[str]:
    downloader = ModelDownloader()
    
    print("\n=== Загрузка модели ===")
    print("Выберите источник:")
    print("1. Hugging Face Hub (рекомендуется)")
    print("2. Прямая ссылка (URL)")
    print("3. Локальный путь")
    
    choice = input("\nВаш выбор (1-3): ").strip()
    
    if choice == '1':
        repo_id = input("Введите ID модели (например, deepseek-ai/deepseek-coder-1.3b): ").strip()
        if not repo_id:
            print("Ошибка: ID модели не может быть пустым")
            return None
        
        revision = input("Версия/ветка (Enter для main): ").strip() or None
        
        result = downloader.download_from_huggingface(repo_id, revision)
        if result['success']:
            print(f"\n✅ Модель успешно загружена в: {result['path']}")
            return result['path']
        else:
            print(f"\n❌ Ошибка: {result['error']}")
            return None
    
    elif choice == '2':
        url = input("Введите URL файла: ").strip()
        if not url:
            print("Ошибка: URL не может быть пустым")
            return None
        
        result = downloader.download_from_url(url)
        if result['success']:
            print(f"\n✅ Файл успешно загружен: {result['path']}")
            return result['path']
        else:
            print(f"\n❌ Ошибка: {result['error']}")
            return None
    
    elif choice == '3':
        local_path = input("Введите локальный путь: ").strip()
        if not local_path:
            print("Ошибка: Путь не может быть пустым")
            return None
        
        result = downloader.download_model_files(local_path, source_type='local')
        if result['success']:
            print(f"\n✅ Модель скопирована в: {result['path']}")
            return result['path']
        else:
            print(f"\n❌ Ошибка: {result['error']}")
            return None
    
    else:
        print("Неверный выбор")
        return None

