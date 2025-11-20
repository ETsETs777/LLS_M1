import sys
import os
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from desktop.utils.model_downloader import download_model_interactive, ModelDownloader
from desktop.utils.logger import get_logger

logger = get_logger('scripts.download_model')


def main():
    print("=" * 60)
    print("  LLS_M1 - Загрузка модели")
    print("=" * 60)
    print()
    model_path = download_model_interactive()
    
    if model_path:
        print("\n" + "=" * 60)
        print("✅ Модель успешно загружена!")
        print(f"📁 Путь: {model_path}")
        print("\nСледующие шаги:")
        print("1. Откройте приложение")
        print("2. Перейдите в Настройки (Ctrl+,)")
        print(f"3. Установите путь к модели: {model_path}")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ Загрузка не завершена")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nЗагрузка прервана пользователем.")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Критическая ошибка: {e}")
        print(f"\n❌ Произошла ошибка: {e}")
        sys.exit(1)

