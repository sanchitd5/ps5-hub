# PS5 Hub

Extensible PlayStation 5 plugin dashboard. Central hub for PS5 exploits, payloads, and tools.

## Features

- **PS5-style UI** — Dark theme, card-based layout, smooth animations
- **Plugin system** — Extensible architecture for adding tools and exploits
- **Keyboard navigation** — Arrow keys + Enter for full PS5 gamepad support
- **Embed support** — Iframe plugins for web-based tools
- **Zero dependencies** — Vanilla HTML/CSS/JS, runs on any browser

## Installation

1. Add this repository to Home Assistant add-ons
2. Install the **PS5 Hub** add-on
3. Start the add-on
4. Configure DNS redirect: `manuals.playstation.net` → Home Assistant IP
5. On PS5, set DNS to Home Assistant IP
6. Open any page that redirects to `manuals.playstation.net` → Hub will load

## Plugin Structure

Each plugin is a JSON entry in `plugins.json`:

```json
{
  "id": "unique-plugin-id",
  "name": "Plugin Name",
  "icon": "icons/icon.png",
  "description": "Brief description",
  "target": "http://192.168.1.3:8000",
  "type": "link"
}
```

### Plugin Types

- **`link`** — Redirect to external URL or service
- **`embed`** — Load in fullscreen iframe (for web tools you control)

### Icon

- Path is relative to `www/` folder
- PNG format (96x96 recommended)
- If missing, shows first letter of plugin name

## Adding Plugins

1. Add entry to `addons/ps5-hub/www/plugins.json`
2. Optionally add icon to `addons/ps5-hub/www/icons/`
3. Rebuild/restart add-on

## Development

Serve locally:

```bash
cd addons/ps5-hub/www
python3 -m http.server 8000
```

Visit: `http://localhost:8000`

## Related

- [PS5 WebKit Autoloader](https://github.com/sanchitd5/ps5-webkit-autoloader) — Exploit loader plugin
- [PS5 Payload Manager](https://github.com/itsPLK/ps5-payload-manager) — Payload delivery service
