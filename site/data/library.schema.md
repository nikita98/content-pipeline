# Формат записи библиотеки (JSON)

Файл — JSON-массив объектов. Одна запись = один инструмент / репозиторий / сервис / модель / ассет-библиотека / референс.

```json
{
  "id": "kebab-case-unique, напр. kajisho5-ffmpeg-skill",
  "name": "Короткое имя",
  "url": "https://...",
  "kind": "skill | plugin | mcp | cli | library | model | service | assets | reference | pipeline",
  "topic": "research | texts | video | publish | orchestration | meta",
  "steps": ["1", "13"],
  "what": "Что делает, 1–2 предложения, сухо.",
  "license": "MIT | Apache-2.0 | AGPL-3.0 | proprietary | unknown ...",
  "price": "free | freemium | paid",
  "price_note": "напр. «ключ YouTube API, бесплатно 10 000 ед./день» или пусто",
  "ru": "yes | partial | no | unknown",
  "ru_note": "что с русским, или пусто",
  "agents": ["claude", "codex", "opencode", "kimi", "deepseek", "any"],
  "stars": 1234,
  "verdict": "take | idea | no | check",
  "verdict_note": "Почему, 1 предложение.",
  "checked": true,
  "source": "откуда узнали: файл отчёта (04a, 04b, 04c, 04d, 05, 06) или «воркшоп», «план»"
}
```

Правила:
- `steps` — номера шагов конвейера: "★" координатор, "0" паспорт, "1" ресёрч, "2" идеи, "3" план и кодовые слова, "4" тексты, "5" карусели, "6" сценарии, "7" раскадровка, "8" генерация, "9" нарезка, "10" монтаж, "11" проверка, "12" публикация, "13" аналитика, "14" лид-магниты, "15" воронка.
- `checked: true` — страницу/README открыли и прочитали; `false` — найдено только поиском.
- `stars` — число или null. `agents` — только подтверждённые; не подтверждено — пустой массив.
- Неизвестно — "unknown" или null, не выдумывать.
- Валидный JSON: без комментариев, без висячих запятых.
