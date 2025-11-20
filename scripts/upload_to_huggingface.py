import sys
import os
from pathlib import Path

try:
    from huggingface_hub import HfApi, login
    from huggingface_hub.utils import HfHubHTTPError
except ImportError:
    print("❌ Ошибка: huggingface_hub не установлен")
    print("Установите: pip install huggingface_hub")
    sys.exit(1)


def upload_model(
    model_dir: str,
    repo_id: str,
    private: bool = False,
    token: Optional[str] = None
):
    model_path = Path(model_dir)
    if not model_path.exists():
        print(f"❌ Ошибка: Директория не найдена: {model_dir}")
        return False
    if token:
        login(token=token)
    else:
        print("Войдите в Hugging Face (откройте браузер):")
        login()
    api = HfApi()
    try:
        try:
            api.create_repo(
                repo_id=repo_id,
                repo_type="model",
                private=private,
                exist_ok=True
            )
            print(f"✅ Репозиторий создан/проверен: {repo_id}")
        except HfHubHTTPError as e:
            print(f"⚠️  Репозиторий уже существует или ошибка: {e}")
        print(f"\n📤 Загрузка модели из {model_dir}...")
        print("Это может занять некоторое время...\n")
        
        api.upload_folder(
            folder_path=str(model_path),
            repo_id=repo_id,
            repo_type="model",
            ignore_patterns=["*.pyc", "__pycache__", ".git"]
        )
        
        print(f"\n✅ Модель успешно загружена!")
        print(f"🔗 URL: https://huggingface.co/{repo_id}")
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка при загрузке: {e}")
        return False


def main():
    print("=" * 60)
    print("  LLS_M1 - Загрузка модели на Hugging Face Hub")
    print("=" * 60)
    print()
    model_dir = input("Путь к директории с моделью [models/]: ").strip() or "models"
    repo_id = input("ID репозитория (username/repo-name): ").strip()
    
    if not repo_id:
        print("❌ Ошибка: ID репозитория обязателен")
        return 1
    
    private_str = input("Приватный репозиторий? (y/N): ").strip().lower()
    private = private_str == 'y'
    success = upload_model(model_dir, repo_id, private=private)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Готово! Модель доступна на Hugging Face Hub")
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
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

