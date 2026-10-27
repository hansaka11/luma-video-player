# Luma Player 🎬

Luma Player is a sleek, lightweight, and feature-rich video player built with Python and PyQt5. It offers a clean user interface with built-in theming, comprehensive subtitle support, and a floating control bar for an immersive full-screen experience.

## ✨ Features

* **Wide Format Support:** Plays `.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`, and many more video formats.
* **Smart Subtitles:** Full support for `.srt`, `.vtt`, `.ass`, and `.ssa` subtitle files. Includes on-the-fly subtitle synchronization (delay/advance) and text size adjustments.
* **Beautiful Themes:** Comes with carefully crafted themes (Normal dark mode and a unique Japanese aesthetic theme).
* **Playlist Management:** Easy drag-and-drop support for files and folders. Automatically detects and loads videos from dropped folders.
* **Playback Controls:** Adjustable playback speed (0.5x to 2.0x), repeat modes (playlist, track, off), and precise seeking.
* **Always on Top:** Pin the player above other windows for distraction-free viewing.
* **Immersive Fullscreen:** Frameless video view with an auto-hiding floating control bar.

## 🚀 Prerequisites

To run this application, you need Python installed on your system along with the `PyQt5` library.

```bash
pip install PyQt5
```

## 🛠️ Installation & Usage

1. Clone the repository or download the project files:
   ```bash
   git clone https://github.com/YourUsername/LumaPlayer.git
   cd LumaPlayer
   ```
2. Run the application:
   ```bash
   python player.py
   ```
3. Press `Ctrl+O` to open video files or simply **drag and drop** videos directly into the player window.

## ⌨️ Keyboard Shortcuts

Luma Player is designed to be fully navigable via keyboard:

| Key | Action |
| :--- | :--- |
| `Space` | Play / Pause |
| `F` | Toggle Full Screen |
| `Esc` | Exit Full Screen |
| `Left` / `Right` | Seek backward/forward by 5 seconds |
| `J` / `K` | Seek backward/forward by 10 seconds |
| `Up` / `Down` | Increase/Decrease Volume |
| `M` | Toggle Mute |
| `C` | Toggle Subtitles |
| `Z` / `X` | Adjust subtitle delay (-100ms / +100ms) |
| `[` / `]` | Decrease/Increase playback speed |
| `N` / `P` | Next / Previous video in playlist |
| `R` | Cycle repeat modes |
| `L` | Show/Hide Playlist |
| `T` | Cycle Themes |
| `Ctrl+O` | Open video files |
| `Ctrl+Shift+O` | Open a folder of videos |

## 🎨 Themes
* **Normal:** Projector room aesthetic with ink-blue blacks and amber lamp accents.
* **Japanese:** Washi paper and sumi ink style with vermilion (shu) seal accents. Use the `T` key to switch!