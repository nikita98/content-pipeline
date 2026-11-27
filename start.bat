@echo off
chcp 65001 >NUL
setlocal
title Конвейер контента — интерфейс
cd /d "%~dp0"
set "SECTION=%~1"
set "PYEXE="
where py >NUL 2>NUL
if not errorlevel 1 (
  py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >NUL 2>NUL
  if not errorlevel 1 set "PYEXE=py -3"
)
if not defined PYEXE (
  where python >NUL 2>NUL
  if not errorlevel 1 (
    python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >NUL 2>NUL
    if not errorlevel 1 set "PYEXE=python"
  )
)
if not defined PYEXE (
  echo.
  echo Не найден Python 3.10 или новее.
  echo Установите его одной командой в PowerShell:
  echo     winget install Python.Python.3.12
  echo или скачайте с https://www.python.org/downloads/ ^(отметьте "Add python.exe to PATH"^).
  echo После установки закройте это окно и запустите start.bat снова.
  echo.
  pause
  exit /b 1
)
echo.
echo Интерфейс конвейера запускается. Браузер откроется сам.
echo НЕ ЗАКРЫВАЙТЕ это окно, пока работаете. Закрыть окно = остановить интерфейс.
echo.
if defined SECTION (
  %PYEXE% "%~dp0app\server.py" --section %SECTION%
) else (
  %PYEXE% "%~dp0app\server.py"
)
echo.
echo Интерфейс остановлен.
pause
