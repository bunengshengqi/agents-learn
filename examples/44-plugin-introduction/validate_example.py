"""验证 Day44 教学插件的最小结构，不安装或启用插件。"""

from __future__ import annotations

import json
import re
from pathlib import Path


PLUGIN_ROOT = Path(__file__).with_name("day44-hello-plugin")
MANIFEST_PATH = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
FRONTMATTER = re.compile(r"\A---\n(?P<body>.*?)\n---\n", re.DOTALL)


def main() -> None:
    """检查 manifest、相对路径和每个 Skill 的必填元数据。"""
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    required = {"name", "version", "description"}
    missing = required - manifest.keys()
    assert not missing, f"manifest 缺少字段：{sorted(missing)}"
    assert manifest["name"] == PLUGIN_ROOT.name, "目录名必须与插件 name 相同"

    skills_path = manifest.get("skills")
    assert isinstance(skills_path, str) and skills_path.startswith("./")
    skills_root = PLUGIN_ROOT / skills_path.removeprefix("./")
    assert skills_root.is_dir(), f"skills 目录不存在：{skills_root}"

    skill_files = sorted(skills_root.glob("*/SKILL.md"))
    assert skill_files, "至少需要一个 skills/<name>/SKILL.md"

    for skill_file in skill_files:
        text = skill_file.read_text(encoding="utf-8")
        match = FRONTMATTER.match(text)
        assert match, f"{skill_file} 缺少 YAML frontmatter"
        metadata = match.group("body")
        assert re.search(r"^name:\s*\S+", metadata, re.MULTILINE)
        assert re.search(r"^description:\s*.+", metadata, re.MULTILINE)

    print("Plugin:", manifest["name"], manifest["version"])
    print("Skills:", [path.parent.name for path in skill_files])
    print("✅ Day44 最小插件结构检查通过（未安装插件）")


if __name__ == "__main__":
    main()
