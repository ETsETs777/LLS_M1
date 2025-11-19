import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt5.QtWidgets import QApplication

from desktop.ui.main_window import MainWindow
from desktop.config.settings import Settings
from desktop.database.db import Database
from desktop.database.repositories.user_repository import UserRepository
from desktop.ui.user.user_dialog import UserDialog


def main():
    app = QApplication(sys.argv)
    settings = Settings()
    database = Database(settings.get_database_path())
    user_repository = UserRepository(database)
    user_dialog = UserDialog(settings, user_repository)
    if user_dialog.exec_() != user_dialog.Accepted:
        database.close()
        return
    window = MainWindow(settings=settings, user_repository=user_repository)
    window.show()
    exit_code = app.exec_()
    database.close()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

