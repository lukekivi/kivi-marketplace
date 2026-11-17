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

`tests/test_plugins.py` — stdlib `unittest`, no dependencies. Validates manifests, SKILL.md frontmatter, and asset reference integrity across all plugins.

```
python3 -m unittest tests/test_plugins.py
```
