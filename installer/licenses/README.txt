Конвейер контента — встроенные программы и их лицензии

Установщик кладёт в папку tools\ переносные программы. Каждая распространяется на своих условиях;
тексты лицензий — в папках рядом (licenses\<программа>\), там же SOURCE.txt: версия, адрес загрузки,
SHA256 и где взять исходный код.

- tools\python      — Python 3.12, сборка python-build-standalone (astral-sh). Лицензия Python — PSF License;
                      в сборке есть OpenSSL (Apache-2.0), Tcl/Tk, SQLite, zlib и др. — тексты в licenses\python.
- tools\ffmpeg      — FFmpeg, сборка «essentials» с gyan.dev. Собрана с --enable-gpl --enable-version3,
                      поэтому распространяется по GNU GPL версии 3 или новее. Исходный код FFmpeg —
                      https://ffmpeg.org/download.html, конфигурация сборки — https://www.gyan.dev/ffmpeg/builds/.
                      Программа запускается как отдельный исполняемый файл, с кодом конвейера не связывается.
- tools\node        — Node.js, лицензия MIT (зависимости — в LICENSE).
- tools\mingit      — MinGit (Git for Windows). Git — GNU GPL версии 2; исходный код —
                      https://github.com/git-for-windows/git.
- tools\auto-editor — auto-editor, Unlicense (общественное достояние).

Пакеты Python (раздел «Установка»: распознавание, озвучка и др.) скачиваются с PyPI и download.pytorch.org
при установке компонентов и распространяются на условиях своих авторов.
