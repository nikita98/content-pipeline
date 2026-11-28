@AGENTS.md

## Только для Claude
- Скиллы разрабатываем со встроенным скиллом skill-creator: черновик, тестовые запросы, прогон со скиллом и без, доработка description.
- Для ресёрча страниц в браузере — Claude in Chrome; в других агентах его заменяет Playwright MCP, поэтому в текстах скиллов пиши «браузер», а не название инструмента.
- Работа идёт в Claude Code (desktop, Windows). Предпросмотр: `.claude/launch.json` — `plan-site` (страница плана, порт 8000) и `app` (интерфейс, порт 8765).
- Веб-страница плана — артефакт https://claude.ai/artifact/6VNrHvwcXVbcU2gBeUGq7B; при публикации передавать её URL, чтобы обновить, а не создать новую. Публикуется `site/index.html` и файлы `site/data/*.json` под теми же путями (`data/...`).
- Страница стенда этапа 3 — отдельный артефакт https://claude.ai/artifact/EZrhygyXB5WRKvHrY9y4eu: `site/bench.html` публикуется как `index.html`, рядом `data/bench.json` и `data/bench_results.json`. После новых результатов: `summary.py`, затем публикация.
