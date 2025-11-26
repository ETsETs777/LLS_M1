@echo off
setlocal
cd /d "%~dp0"
set "NEED_INSTALL="
set "VENV_DIR=.venv"
set "PYTHON=%VENV_DIR%\Scripts\python.exe"
if not exist "%PYTHON%" (
    if not exist "%VENV_DIR%" (
        echo [INFO] Создание виртуального окружения...
    ) else (
        echo [INFO] Пересоздание виртуального окружения...
    )
    py -3 -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERROR] Не удалось создать виртуальное окружение
        exit /b 1
    )
    set "NEED_INSTALL=1"
)
if /i "%~1"=="--reinstall" (
    echo [INFO] Принудительная переустановка зависимостей
    del /q "%VENV_DIR%\.deps_ready" 2>nul
    set "NEED_INSTALL=1"
)
if not exist requirements.txt (
    echo [ERROR] Файл requirements.txt не найден
    exit /b 1
)
if not exist "%VENV_DIR%\.deps_ready" set "NEED_INSTALL=1"
if defined NEED_INSTALL (
    echo [INFO] Установка зависимостей, требуется интернет...
    call "%PYTHON%" -m pip install --upgrade pip
    if errorlevel 1 (
        echo [ERROR] Не удалось обновить pip
        exit /b 1
    )
    call "%PYTHON%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Не удалось установить зависимости
        exit /b 1
    )
    > "%VENV_DIR%\.deps_ready" echo %date% %time%
)
set PYTHONUTF8=1
echo [INFO] Запуск приложения...
call "%PYTHON%" desktop\main.py
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
    echo [ERROR] Приложение завершилось с кодом %EXIT_CODE%
)
exit /b %EXIT_CODE%

