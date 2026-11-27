"""Копирует скиллы из skills/ в папки агентов этого репозитория.

  python tools/install_skills.py            # все скиллы
  python tools/install_skills.py kp-bench   # один

Claude Code читает .claude/skills/, Codex, Kimi Code и OpenCode — .agents/skills/.
Папка evals/ не копируется.
"""
import shutil
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
names = sys.argv[1:] or [p.name for p in (root / "skills").iterdir() if (p / "SKILL.md").is_file()]
for name in names:
    src = root / "skills" / name
    if not (src / "SKILL.md").is_file():
        sys.exit(f"Нет скилла {name}")
    for dst_root in (root / ".claude" / "skills", root / ".agents" / "skills"):
        dst = dst_root / name
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("evals", "__pycache__"))
    print(f"{name}: .claude/skills и .agents/skills")
