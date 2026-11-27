#!/bin/bash
# Интерфейс конвейера контента для macOS. Первый запуск: правый клик → Открыть (или chmod +x start.command).
cd "$(dirname "$0")" || exit 1
SECTION="$1"
PY=""
for c in python3 python3.12 python3.13 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
    PY="$c"; break
  fi
done
if [ -z "$PY" ]; then
  echo
  echo "Не найден Python 3.10 или новее."
  echo "Установите: brew install python@3.12  (или с https://www.python.org/downloads/)"
  echo "Потом запустите start.command снова."
  read -r -p "Нажмите Enter, чтобы закрыть окно…" _
  exit 1
fi
echo
echo "Интерфейс конвейера запускается. Браузер откроется сам."
echo "НЕ ЗАКРЫВАЙТЕ это окно, пока работаете. Закрыть окно = остановить интерфейс."
echo
if [ -n "$SECTION" ]; then
  "$PY" "app/server.py" --section "$SECTION"
else
  "$PY" "app/server.py"
fi
echo
read -r -p "Интерфейс остановлен. Нажмите Enter, чтобы закрыть окно…" _
