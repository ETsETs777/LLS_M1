"""
Точка входа в приложение.
Обрабатывает запуск и инициализацию главного окна.
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

from desktop.ui.main_window import MainWindow
from desktop.utils.logger import get_logger

logger = get_logger('desktop.main')


def main() -> int:
    """
    Главная функция приложения.
    
    Returns:
        Код выхода (0 при успешном завершении)
    """
    try:
        logger.info("Запуск приложения")
        
        # Настройка Qt приложения
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        app = QApplication(sys.argv)
        app.setApplicationName("LLS_M1")
        app.setOrganizationName("ETsETs777")
        
        # Создание и показ главного окна
        try:
            window = MainWindow()
            window.show()
            logger.info("Главное окно успешно создано и отображено")
        except Exception as e:
            logger.exception(f"Ошибка при создании главного окна: {e}")
            QMessageBox.critical(
                None,
                'Ошибка запуска',
                f'Не удалось создать главное окно:\n{str(e)}\n\nПроверьте логи для подробностей.'
            )
            return 1
        
        # Запуск главного цикла приложения
        exit_code = app.exec_()
        logger.info(f"Приложение завершено с кодом: {exit_code}")
        return exit_code
        
    except KeyboardInterrupt:
        logger.info("Приложение прервано пользователем (Ctrl+C)")
        return 0
    except Exception as e:
        logger.exception(f"Критическая ошибка при запуске приложения: {e}")
        try:
            QMessageBox.critical(
                None,
                'Критическая ошибка',
                f'Произошла критическая ошибка:\n{str(e)}\n\nПриложение будет закрыто.\n\nПроверьте логи для подробностей.'
            )
        except Exception:
            # Если даже QMessageBox не работает, выводим в консоль
            print(f"Критическая ошибка: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

