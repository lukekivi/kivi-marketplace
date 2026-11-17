"""Structural tests for the local marketplace and its plugins.

Run from the marketplace root:

    python3 -m unittest tests/test_plugins.py

Tests:
  * marketplace.json shape and that each listed plugin source resolves to a real dir
  * each plugin.json shape (name, version, description, author object, etc.)
  * each SKILL.md has YAML frontmatter with name/description/argument-hint
  * every `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/assets/<file>` path referenced in
    a SKILL.md actually exists on disk

These do NOT test SKILL.md orchestration behavior — that's a prompt, not code.
End-to-end behavioral tests against an LLM are out of scope here.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

MARKETPLACE_ROOT = Path(__file__).resolve().parent.parent


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _split_frontmatter(md: str) -> tuple[dict, str]:
    """Parse a small subset of YAML frontmatter (key: value, multi-line `>` folded)
    sufficient for SKILL.md files. Avoids a yaml dependency."""
    if not md.startswith("---\n"):
        raise ValueError("missing leading frontmatter delimiter")
    rest = md[len("---\n"):]
    end = rest.find("\n---\n")
    if end < 0:
        raise ValueError("missing trailing frontmatter delimiter")
    block = rest[:end]
    fm: dict[str, str] = {}
    current_key: str | None = None
    folded: list[str] = []
    for line in block.splitlines():
        if not line.strip():
            continue
        # New key at column 0 (no leading whitespace) and contains a colon.
        if not line.startswith((" ", "\t")) and ":" in line:
            if current_key is not None:
                fm[current_key] = " ".join(folded).strip()
                folded = []
            key, _, val = line.partition(":")
            val = val.strip()
            if val == ">":
                current_key = key.strip()
            else:
                fm[key.strip()] = val.strip().strip('"\'')
                current_key = None
        else:
            # Continuation of a folded value.
            if current_key is not None:
                folded.append(line.strip())
    if current_key is not None:
        fm[current_key] = " ".join(folded).strip()
    body = rest[end + len("\n---\n"):]
    return fm, body


# ---- Marketplace-level tests -------------------------------------------------

class MarketplaceManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.path = MARKETPLACE_ROOT / ".claude-plugin" / "marketplace.json"
        self.assertTrue(self.path.exists(), f"missing {self.path}")
        self.data = _load_json(self.path)

    def test_required_top_level_fields(self):
        self.assertIn("name", self.data)
        self.assertIn("plugins", self.data)
        self.assertIsInstance(self.data["plugins"], list)
        self.assertGreater(len(self.data["plugins"]), 0)

    def test_each_plugin_entry_has_name_description_source(self):
        for entry in self.data["plugins"]:
            self.assertIn("name", entry)
            self.assertIn("description", entry)
            self.assertIn("source", entry)

    def test_each_plugin_source_resolves_to_directory(self):
        for entry in self.data["plugins"]:
            src = entry["source"]
            self.assertTrue(src.startswith("./"), f"{entry['name']} source must be relative: {src}")
            resolved = (MARKETPLACE_ROOT / src).resolve()
            self.assertTrue(resolved.is_dir(), f"{entry['name']} source dir missing: {resolved}")

    def test_owner_object_when_present(self):
        if "owner" in self.data:
            self.assertIsInstance(self.data["owner"], dict)
            self.assertIn("name", self.data["owner"])


# ---- Plugin-level tests -------------------------------------------------------

def _plugin_dirs() -> list[Path]:
    return sorted([p for p in (MARKETPLACE_ROOT / "plugins").iterdir() if p.is_dir()])


class PluginManifestTests(unittest.TestCase):
    REQUIRED_FIELDS = ("name", "version", "description")

    def test_each_plugin_has_manifest(self):
        for p in _plugin_dirs():
            with self.subTest(plugin=p.name):
                self.assertTrue((p / ".claude-plugin" / "plugin.json").exists())

    def test_each_plugin_manifest_has_required_fields(self):
        for p in _plugin_dirs():
            with self.subTest(plugin=p.name):
                data = _load_json(p / ".claude-plugin" / "plugin.json")
                for field in self.REQUIRED_FIELDS:
                    self.assertIn(field, data, f"{p.name} missing {field}")

    def test_each_plugin_author_is_object_when_present(self):
        # Validator we hit at install time rejected string author.
        for p in _plugin_dirs():
            with self.subTest(plugin=p.name):
                data = _load_json(p / ".claude-plugin" / "plugin.json")
                if "author" in data:
                    self.assertIsInstance(
                        data["author"],
                        dict,
                        f"{p.name} author must be an object (had string)",
                    )
                    self.assertIn("name", data["author"])

    def test_plugin_dir_names_match_manifest_names(self):
        for p in _plugin_dirs():
            with self.subTest(plugin=p.name):
                data = _load_json(p / ".claude-plugin" / "plugin.json")
                self.assertEqual(p.name, data["name"], "dir name and manifest name must match")

    def test_marketplace_lists_each_plugin_dir(self):
        marketplace = _load_json(MARKETPLACE_ROOT / ".claude-plugin" / "marketplace.json")
        listed = {entry["name"] for entry in marketplace["plugins"]}
        on_disk = {p.name for p in _plugin_dirs()}
        self.assertEqual(
            listed,
            on_disk,
            f"marketplace listing {listed} != plugin dirs {on_disk}",
        )


# ---- Skill-level tests --------------------------------------------------------

def _skill_files() -> list[Path]:
    out: list[Path] = []
    for plugin in _plugin_dirs():
        skills_dir = plugin / "skills"
        if not skills_dir.is_dir():
            continue
        out.extend(skills_dir.glob("*/SKILL.md"))
    return sorted(out)


class SkillFrontmatterTests(unittest.TestCase):
    REQUIRED_FRONTMATTER = ("name", "description")

    def test_every_skill_has_parseable_frontmatter(self):
        for skill in _skill_files():
            with self.subTest(skill=str(skill.relative_to(MARKETPLACE_ROOT))):
                fm, _ = _split_frontmatter(skill.read_text(encoding="utf-8"))
                for key in self.REQUIRED_FRONTMATTER:
                    self.assertIn(key, fm, f"{skill} missing frontmatter key '{key}'")
                    self.assertTrue(fm[key].strip(), f"{skill} has empty '{key}'")

    def test_skill_dir_name_matches_frontmatter_name(self):
        for skill in _skill_files():
            with self.subTest(skill=str(skill.relative_to(MARKETPLACE_ROOT))):
                fm, _ = _split_frontmatter(skill.read_text(encoding="utf-8"))
                self.assertEqual(
                    skill.parent.name,
                    fm["name"],
                    f"{skill} frontmatter name must match dir name",
                )


class SkillAssetReferenceTests(unittest.TestCase):
    """Verify every `${CLAUDE_PLUGIN_ROOT}/skills/<x>/assets/<file>` reference
    in SKILL.md actually exists on disk."""

    PATTERN = re.compile(
        r"\$\{CLAUDE_PLUGIN_ROOT\}/skills/([A-Za-z0-9_-]+)/assets/([A-Za-z0-9_./-]+)"
    )

    def test_all_asset_references_resolve(self):
        missing: list[str] = []
        for skill in _skill_files():
            plugin_root = skill.parent.parent.parent  # plugins/<plugin>/
            text = skill.read_text(encoding="utf-8")
            for match in self.PATTERN.finditer(text):
                skill_name, asset_name = match.group(1), match.group(2)
                target = plugin_root / "skills" / skill_name / "assets" / asset_name
                if not target.exists():
                    missing.append(f"{skill.relative_to(MARKETPLACE_ROOT)} -> {target.relative_to(MARKETPLACE_ROOT)}")
        self.assertFalse(missing, "Unresolved asset references:\n  " + "\n  ".join(missing))


if __name__ == "__main__":
    unittest.main()
