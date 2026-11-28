# claude-plugins

A catalog of Claude Code plugins by José Silva. Each plugin lives in its own repository; this repo only lists them.

## Add the catalog

```
/plugin marketplace add zepedrosilva/claude-plugins
```

## Plugins

| Plugin | Install | What it does |
|---|---|---|
| [brand-studio](https://github.com/zepedrosilva/brand-studio) | `/plugin install brand-studio@zepedrosilva` | Drafts a brand identity for your app as checked SVG, for developers without a design background, and reviews existing SVG logos against numbered, sourced rules |
| [viz-advisor](https://github.com/zepedrosilva/viz-advisor) | `/plugin install viz-advisor@zepedrosilva` | Decides which visual to use in a presentation or an application, and reviews visuals already chosen |
| [deckhand](https://github.com/zepedrosilva/deckhand) | `/plugin install deckhand@zepedrosilva` | Plans, builds and reviews Stream Deck plugins with the official Elgato SDK |

## Website

This repo publishes [zepedro.com/plugins](https://zepedro.com/plugins/): an index built from the catalog, and each plugin's site under `/plugins/<name>/`. A plugin gets a site by shipping `scripts/build-site.sh <out-dir>` in its own repository. The hub runs that script only for repositories owned by `zepedrosilva`. It rebuilds on every push here, daily, and when run by hand from the Actions tab.

## Adding a plugin

Add one entry to [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) with a `git-subdir` or `github` source pointing at the plugin's repository, then run `claude plugin validate .`. Versions come from each plugin's own `plugin.json`, so this file has no `version` fields.

## Licence

[MIT](LICENSE). Each plugin carries its own licence in its repository.
