# DeckForge

**Desktop Mode, Unleashed.**

DeckForge is a Steam Deck desktop optimizer app built with PySide6. It gives you gaming-level performance in Desktop Mode without switching back and forth.

## Features

- **Performance Tuning** — Set CPU governor, kill background tasks, tune swappiness
- **RGB Control** — Full OpenRGB integration for mouse and keyboard
- **ChromaSync** — Real-time screen-reactive RGB at ~24fps using ffmpeg pipe capture
- **Process Manager** — Kill KDE bloat to free RAM
- **Profiles** — One-click Performance / Balanced / Battery Saver presets
- **Dark/Light theme**

## Requirements

- Steam Deck (SteamOS) in Desktop Mode
- OpenRGB (Flatpak): `flatpak install org.openrgb.OpenRGB`
- Python deps: `pip install PySide6 openrgb-python pillow numpy --break-system-packages`

## Install

```bash
git clone https://github.com/YOURUSERNAME/DeckForge
cd DeckForge
python3 main.py
```

## Devices Tested

- Logitech G502 HERO
- Razer BlackWidow Chroma Tournament Edition

## License

MIT
