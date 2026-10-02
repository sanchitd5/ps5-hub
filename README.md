# PS5 Hub Repository

Home Assistant add-on repository for PS5 Hub — extensible PlayStation 5 plugin dashboard.

## What is PS5 Hub?

PS5 Hub is a central dashboard for managing PS5 exploits, payloads, and tools. It provides a plugin system for easily extending functionality and integrates with other PS5 services.

Besides the dashboard (ports 443/80, also the `manuals.playstation.net` DNS-rewrite target), the add-on bundles three exploit-delivery plugins fetched fresh from their upstream repos at image build time — no forks, no vendoring:

- WebKit Autoloader (port 8082) — built from [itsPLK/ps5-webkit-autoloader](https://github.com/itsPLK/ps5-webkit-autoloader)
- Relapse Exploit (port 8083) — from [ntfargo/Relapse-Exploit](https://github.com/ntfargo/Relapse-Exploit)
- Relapse (soniciso1) (port 8084) — from [soniciso1/relapse](https://github.com/soniciso1/relapse)

## Installation

1. Open Home Assistant
2. Go to Settings → Add-ons → Repositories
3. Add this repository: `https://github.com/sanchitd5/ps5-hub`
4. Install **PS5 Hub** from the repository

## Available Add-ons

- **PS5 Hub** — Central dashboard with plugin system

## License

GPL-3.0
