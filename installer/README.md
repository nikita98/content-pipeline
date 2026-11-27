# Windows-установщик

`ContentPipeline-Setup-<версия>.exe` — один файл для людей без консоли: «Далее» → папка → галочки → полоса → «Готово» → ярлык на рабочем столе → интерфейс в браузере. Собирается в GitHub Actions (`.github/workflows/build-installer.yml`), лежит в artifacts прогона, а для тега `v*` — в Releases.

## Как устроено
- **Inno Setup 6**, `installer/ContentPipeline.iss`. Установка для текущего пользователя, `PrivilegesRequired=lowest`, без UAC. Папка по умолчанию — `%LOCALAPPDATA%\Programs\ContentPipeline`. Если в пути есть русские буквы, мастер предупреждает и даёт продолжить. Под полем папки — свободное место на диске.
- **Переносные программы** в `tools\` папки установки — по `installer/deps.json` (версия, адрес, SHA256): Python 3.12 (python-build-standalone, с pip, venv и tkinter), ffmpeg + ffprobe (essentials, gyan.dev), Node.js 24 LTS, MinGit, auto-editor. Скачиваются только при сборке; у пользователя установщик ничего не качает, кроме компонентов pip.
- **Компоненты** — `app/setup/components.json`: id, название, описание, объём, окружение (venv), шаги pip и git clone, «только NVIDIA», вкл. по умолчанию. Из него при сборке генерируются секция `[Components]` и описания под списком (`installer/build/components*.iss`). Строка Qwen3-TTS отключается в мастере, если нет `nvidia-smi`.
- **Окно «Установка компонентов»** — `app/setup/components.py` на tkinter из встроенного Python, запуск из `[Run]` через `pythonw.exe` (без консоли). Общая полоса (N из M), текущий пункт («Скачиваю PyTorch для процессора, ≈ … ГБ»), полоса скачивания по `pip --progress-bar raw` (если pip её не знает — бегущая полоса), лог под «Подробнее», «Отмена», итог «установлено / уже было / ошибка» и «Открыть интерфейс». В тихой установке то же самое идёт с `--headless`. Если tkinter не запустится, выбранное пишется в `data\setup\pending.json` и открывается раздел «Установка» в браузере.
  Почему tkinter, а не страница в браузере: окно работает, пока установщик ждёт, без сервера и порта, и не зависит от браузера по умолчанию; tkinter входит в сборку python-build-standalone для Windows (проверяется в смоуке).
- **Окружения и модели** — внутри папки установки, в `data\`: `data\venv\asr`, `data\venv\whisperx`, `data\venv\tts`, `HF_HOME=data\models\huggingface`, `TORCH_HOME=data\models\torch`, `PIP_CACHE_DIR=data\cache\pip`, кэш npm. Выбор диска D: переносит туда всё тяжёлое. Задаёт `app/core/bundled.py`.
- **Ярлыки** (рабочий стол и «Пуск») — `tools\python\pythonw.exe app\server.py`, без чёрного окна. В интерфейсе кнопка «Выход»; сервер сам останавливается, если браузер 10 минут не присылал запросов и нет идущей задачи. Повторный клик по ярлыку открывает браузер на уже работающий сервер (`data\server.lock`: порт, токен, instance). Вывод сервера под pythonw — `data\logs\server.log`.
- **Удаление** — штатное («Параметры → Приложения» или ярлык в «Пуске»). Деинсталлятор останавливает интерфейс (файл `data\stop.request`) и спрашивает, удалить ли `data\` (окружения и модели). Записи и результаты в `bench\` остаются.
- **Отличия установленной копии от git-клона**: рядом лежит `installed.json`; кнопка «Отправить в git» скрыта, основной путь — «Скачать архивом» (решение 22). Копия из git (`start.bat`, `start.command`) работает как раньше: системные программы, окружения `.venv-*` в корне.

Чего нет специально (частые причины ложных срабатываний антивирусов): VBS, скрытые загрузки PowerShell, `ExecutionPolicy Bypass`, упаковщики вроде PyInstaller, обфускация. Установщик и ярлыки запускают только файлы из папки установки.

## Сборка локально на Windows
Нужны Python 3.10+ и Inno Setup 6 (`winget install JRSoftware.InnoSetup` или `choco install innosetup`).
```
python installer/build.py --version 0.1.0
```
Результат — `installer/build/out/ContentPipeline-Setup-0.1.0.exe`. Скачанное кэшируется в `installer/cache/`, хэши проверяются при каждой сборке. Без Inno Setup (проверка подготовки файлов, в том числе на Linux и macOS): `--no-compile`, без скачивания программ — `--no-fetch`.

Смоук-тест на своей машине (ставит в указанную папку и удаляет): `pwsh installer/smoke.ps1 -Setup installer\build\out\ContentPipeline-Setup-0.1.0.exe -Dir C:\cp-test`.

Тихая установка: `ContentPipeline-Setup-0.1.0.exe /VERYSILENT /SUPPRESSMSGBOXES /DIR="D:\ContentPipeline" /COMPONENTS=base,text,stress,edgetts`.

## Обновить версию программы
1. Новая версия, адрес и пустой `sha256` в `installer/deps.json`.
2. `python installer/fetch_deps.py --only <id> --print-hashes --allow-unpinned` — скачает и напечатает SHA256. Если у программы есть `sums_url` (Python, Node), хэш сверяется с опубликованным.
3. Вписать хэш, собрать, прогнать смоук (push в ветку `installer` или ручной запуск workflow).

Адреса: Python — releases `astral-sh/python-build-standalone` (`cpython-3.12.*-x86_64-pc-windows-msvc-install_only.tar.gz`); ffmpeg — releases `GyanD/codexffmpeg` (`ffmpeg-<версия>-essentials_build.zip`); Node — `https://nodejs.org/dist/v<версия>/node-v<версия>-win-x64.zip`; MinGit — releases `git-for-windows/git` (`MinGit-<версия>-64-bit.zip`); auto-editor — releases `WyattBlue/auto-editor` (`auto-editor-windows-x86_64.exe`).

Объёмы компонентов (`size_mb` в `components.json`) — `python installer/probe_sizes.py` на Windows с Python 3.12 (в CI: ручной запуск workflow с галочкой probe или `[probe]` в сообщении коммита). Это объём скачивания колёс pip без моделей; на диске после распаковки больше.

## Выпуск
Тег `v<версия>` на коммите с зелёной сборкой → workflow собирает, проверяет и публикует exe в Releases. Ссылка для пользователей — https://github.com/nikita98/content-pipeline/releases/latest.

## Лицензии встроенных программ
Тексты кладутся в установку, в `licenses\<программа>\`, там же `SOURCE.txt` (версия, адрес, SHA256, исходный код). Общая записка — `installer/licenses/README.txt`.

| Программа | Лицензия | Сборка |
|---|---|---|
| Python 3.12 | PSF License; в сборке OpenSSL (Apache-2.0), Tcl/Tk, SQLite, zlib и др. | python-build-standalone |
| FFmpeg | GPL-3.0-or-later | gyan.dev essentials (`--enable-gpl --enable-version3`). LGPL-сборка — BtbN `*-lgpl-*`; essentials выбран из-за постоянных адресов релизов |
| Node.js | MIT | nodejs.org |
| Git (MinGit) | GPL-2.0 | Git for Windows |
| auto-editor | Unlicense | релиз WyattBlue/auto-editor |

ffmpeg и git запускаются как отдельные программы и с кодом конвейера не связываются. Для GPL при распространении — тексты лицензий и ссылка на исходный код (есть в `licenses\`).

## Не проверено
- Реальная установка тяжёлых компонентов (PyTorch, GigaAM, WhisperX, DeepFilterNet, Qwen3-TTS) в CI не ставится — только план (`--dry-run`) и объёмы.
- SmartScreen и антивирусы: файл не подписан. Для «Неизвестный издатель» без предупреждения нужна подпись кода (сертификат владельца).
- Ручной проход мастера человеком, окно компонентов на экране, масштаб 125–150 %.
- Длинные пути: глубоко вложенные пакеты в `data\venv` при длинной папке установки могут упереться в 260 символов — проверить на WhisperX.
