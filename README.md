# kivi-marketplace

Claude Code plugins for personal workflows.

## Install

```
/plugin marketplace add lukekivi/kivi-marketplace
/plugin install kivi-sdlc@kivi
```

## Plugins

| Plugin | Purpose |
|---|---|
| [kivi-sdlc](plugins/kivi-sdlc) | Personal SDLC workflow: `/recon`, `/plan`, `/work`, `/respond`, `/carve`, `/warroom`, `/uav` |

## Adding a new plugin

1. Create `plugins/<name>/.claude-plugin/plugin.json` and `plugins/<name>/skills/...`.
2. Add an entry to `.claude-plugin/marketplace.json` under `plugins`.
3. `/plugin install <name>@kivi`.

## Conventions

- Plugins ship their own assets under `skills/<skill>/assets/`.

## Tests

`tests/test_plugins.py` — stdlib `unittest`, no dependencies. Validates manifests (and that marketplace descriptions match them), SKILL.md frontmatter, and that every `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_SKILL_DIR}` path referenced in plugin markdown resolves.

```
python3 -m unittest tests/test_plugins.py
```
