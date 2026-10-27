import bisect
import html
import os
import re
import sys
import time

from PyQt5.QtCore import QPoint, QPointF, QRectF, QSettings, QSize, Qt, QTimer, QUrl, pyqtSignal
from PyQt5.QtGui import (
    QColor,
    QCursor,
    QIcon,
    QKeySequence,
    QPainter,
    QPen,
    QPixmap,
    QPolygonF,
)
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QPushButton,
    QShortcut,
    QSizePolicy,
    QSlider,
    QStackedLayout,
    QStyle,
    QVBoxLayout,
    QWidget,
)

# ---------------------------------------------------------------- themes
SANS = '"Segoe UI", "Inter", "Helvetica Neue", sans-serif'
JP_SANS = '"Yu Gothic UI", "Hiragino Sans", "Noto Sans JP", "Meiryo UI", "Segoe UI", sans-serif'
JP_SERIF = '"Yu Mincho", "Hiragino Mincho ProN", "Noto Serif JP", "MS Mincho", Georgia, serif'

THEMES = {
    # Projector room: ink-blue blacks, warm off-white text, amber lamp accent.
    "Normal": {
        "bg": "#0c0d12", "panel": "#14161d", "raised": "#1c1f29", "line": "#272b37",
        "text": "#ece9e2", "muted": "#8b8f9c", "accent": "#f2a93b", "acchov": "#ffbd5c",
        "ink": "#1a1206", "hover": "#262a36", "border2": "#353a49", "stage": "#050608",
        "tint": "rgba(242, 169, 59, 0.16)", "handle": "#ece9e2", "handleb": "#f2a93b",
        "font": SANS, "brandfont": SANS, "brandsize": "14px",
        "rpanel": "12px", "rbottom": "16px", "rbtn": "10px", "rvideo": "14px", "rlogo": "8px",
        "headeredge": "1px solid #272b37", "bottomedge": "1px solid #272b37", "seal": False,
    },
    # Washi paper, sumi ink, vermilion (shu) seal. Square, quiet, thin lines.
    "Japanese": {
        "bg": "#ebe4d2", "panel": "#f6f1e4", "raised": "#ece4d0", "line": "#cdc2a6",
        "text": "#1f1b17", "muted": "#7b705e", "accent": "#c2352b", "acchov": "#d6463a",
        "ink": "#fbf6ea", "hover": "#e2d8c0", "border2": "#b8ab8c", "stage": "#14120f",
        "tint": "rgba(194, 53, 43, 0.12)", "handle": "#c2352b", "handleb": "#f6f1e4",
        "font": JP_SANS, "brandfont": JP_SERIF, "brandsize": "16px",
        "rpanel": "4px", "rbottom": "6px", "rbtn": "3px", "rvideo": "2px", "rlogo": "3px",
        "headeredge": "2px solid #c2352b", "bottomedge": "2px solid #c2352b", "seal": True,
    },
}
C = dict(THEMES["Normal"])  # the active palette; icons and widgets read from here

STYLE_TEMPLATE = """
QMainWindow, QWidget#root { background: @bg; color: @text; }
QWidget { font-family: @font; font-size: 13px; }
QLabel { background: transparent; color: @text; }
QLabel#brand { font-family: @brandfont; font-size: @brandsize; font-weight: 700; }
QLabel#muted, QLabel#time, QLabel#hint, QLabel#status, QLabel#count { color: @muted; }
QLabel#time { font-size: 12px; font-weight: 600; }
QLabel#panel_title { font-family: @brandfont; font-size: 14px; font-weight: 700; }
QLabel#logo {
    background: @accent; border-radius: @rlogo; color: @ink;
    font-family: @brandfont; font-size: 16px; font-weight: 700;
}
QLabel#empty { color: @muted; font-size: 13px; }
QLabel#stage_empty { color: #a9a49a; font-size: 13px; }

QFrame#header {
    background: @panel; border: 1px solid @line; border-bottom: @headeredge; border-radius: @rpanel;
}
QFrame#bottom {
    background: @panel; border: 1px solid @line; border-top: @bottomedge; border-radius: @rbottom;
}
QFrame#dropdown { background: @panel; border: 1px solid @border2; border-radius: @rpanel; }
QFrame#videoframe { background: @stage; border: 1px solid @line; border-radius: @rvideo; }

QPushButton {
    background: @raised; color: @text; border: 1px solid @line;
    border-radius: @rbtn; padding: 8px 14px; font-weight: 600;
}
QPushButton:hover { background: @hover; border-color: @border2; }
QPushButton:pressed { background: @panel; }
QPushButton:checked { border-color: @accent; color: @accent; }
QPushButton#primary { background: @accent; color: @ink; border: none; padding: 9px 16px; }
QPushButton#primary:hover { background: @acchov; }
QPushButton#tool { background: transparent; border: none; padding: 0; border-radius: @rbtn; }
QPushButton#tool:hover { background: @raised; }
QPushButton#tool:pressed { background: @line; }
QPushButton#tool:checked { background: @tint; }
QPushButton#play { background: @accent; border: none; border-radius: 28px; padding: 0; }
QPushButton#play:hover { background: @acchov; }
QPushButton#seg_l, QPushButton#seg_r {
    background: transparent; color: @muted; border: 1px solid @line; padding: 0 12px;
}
QPushButton#seg_l { border-top-right-radius: 0; border-bottom-right-radius: 0; }
QPushButton#seg_r { border-top-left-radius: 0; border-bottom-left-radius: 0; border-left: none; }
QPushButton#seg_l:hover, QPushButton#seg_r:hover { background: @raised; color: @text; }
QPushButton#seg_l:checked, QPushButton#seg_r:checked {
    background: @accent; color: @ink; border-color: @accent;
}

QComboBox {
    background: @raised; color: @text; border: 1px solid @line;
    border-radius: @rbtn; padding: 7px 12px; min-width: 52px; font-weight: 600;
}
QComboBox:hover { border-color: @border2; }
QComboBox QAbstractItemView {
    background: @panel; color: @text; border: 1px solid @line; outline: 0;
    selection-background-color: @accent; selection-color: @ink;
}

QListWidget { background: transparent; border: none; outline: 0; }
QListWidget::item { padding: 10px 12px; border-radius: @rbtn; margin: 1px 0; color: @text; }
QListWidget::item:hover { background: @raised; }
QListWidget::item:selected { background: @tint; color: @text; }

QSlider::groove:horizontal { height: 5px; background: @line; border-radius: 2px; }
QSlider::sub-page:horizontal { background: @accent; border-radius: 2px; }
QSlider::handle:horizontal {
    width: 14px; margin: -5px 0; background: @handle;
    border: 2px solid @handleb; border-radius: 7px;
}
QSlider::handle:horizontal:hover { background: @acchov; }

QScrollBar:vertical { background: transparent; width: 8px; margin: 2px; }
QScrollBar::handle:vertical { background: @line; border-radius: 3px; min-height: 28px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QMenu { background: @panel; border: 1px solid @border2; border-radius: @rpanel; padding: 6px; }
QMenu::item { padding: 8px 22px; border-radius: @rbtn; color: @text; }
QMenu::item:selected { background: @tint; }
QMenu::item:disabled { color: @muted; }
QMenu::separator { height: 1px; background: @line; margin: 6px 8px; }
QToolTip { background: @raised; color: @text; border: 1px solid @border2; padding: 5px 8px; }
"""


def build_style():
    """Fill the template with the active palette (longest names first so @tint never eats @tint2)."""
    style = STYLE_TEMPLATE
    for key in sorted(C, key=len, reverse=True):
        style = style.replace("@" + key, str(C[key]))
    return style


VIDEO_EXTS = (".mp4", ".mkv", ".avi", ".mov", ".wmv", ".m4v", ".webm", ".flv", ".mpg", ".mpeg", ".ts")
SPEEDS = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
REPEAT_OFF, REPEAT_ALL, REPEAT_ONE = 0, 1, 2
SUB_EXTS = (".srt", ".vtt", ".ass", ".ssa")
SUB_SIZES = [16, 20, 24, 28, 34, 42]
UNSET = -2
REPEAT_NAMES = {REPEAT_OFF: "off", REPEAT_ALL: "playlist", REPEAT_ONE: "current video"}


# ---------------------------------------------------------------- icons
def make_icon(name, color=None):
    """Draw a crisp vector icon on a 24x24 grid (rendered at 2x for sharp edges)."""
    col = QColor(color or C["text"])
    pm = QPixmap(48, 48)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.scale(2, 2)
    stroke = QPen(col, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

    def poly(*pts):
        p.setPen(Qt.NoPen)
        p.setBrush(col)
        p.drawPolygon(QPolygonF([QPointF(x, y) for x, y in pts]))

    def line(*pts):
        p.setPen(stroke)
        p.setBrush(Qt.NoBrush)
        p.drawPolyline(QPolygonF([QPointF(x, y) for x, y in pts]))

    def block(x, y, w, h, r=1.5):
        p.setPen(Qt.NoPen)
        p.setBrush(col)
        p.drawRoundedRect(QRectF(x, y, w, h), r, r)

    speaker = [(4, 9), (8, 9), (13, 5), (13, 19), (8, 15), (4, 15)]

    if name == "play":
        poly((8, 4), (20, 12), (8, 20))
    elif name == "pause":
        block(6, 4, 4, 16)
        block(14, 4, 4, 16)
    elif name == "stop":
        block(6, 6, 12, 12, 2)
    elif name == "prev":
        block(5, 5, 2.5, 14)
        poly((19, 5), (19, 19), (9, 12))
    elif name == "next":
        block(16.5, 5, 2.5, 14)
        poly((5, 5), (5, 19), (15, 12))
    elif name in ("volume", "mute"):
        poly(*speaker)
        p.setPen(stroke)
        p.setBrush(Qt.NoBrush)
        if name == "volume":
            p.drawArc(QRectF(10, 8, 7, 8), -55 * 16, 110 * 16)
            p.drawArc(QRectF(8, 4, 13, 16), -55 * 16, 110 * 16)
        else:
            line((16, 9), (22, 15))
            line((22, 9), (16, 15))
    elif name == "fullscreen":
        line((4, 9), (4, 4), (9, 4))
        line((15, 4), (20, 4), (20, 9))
        line((4, 15), (4, 20), (9, 20))
        line((20, 15), (20, 20), (15, 20))
    elif name == "exit_fullscreen":
        line((9, 4), (9, 9), (4, 9))
        line((15, 4), (15, 9), (20, 9))
        line((4, 15), (9, 15), (9, 20))
        line((20, 15), (15, 15), (15, 20))
    elif name in ("repeat", "repeat_one"):
        line((4, 12), (4, 9), (7, 7), (17, 7))
        poly((16, 3.5), (21, 7), (16, 10.5))
        line((20, 12), (20, 15), (17, 17), (7, 17))
        poly((8, 13.5), (3, 17), (8, 20.5))
        if name == "repeat_one":
            f = p.font()
            f.setPixelSize(8)
            f.setBold(True)
            p.setFont(f)
            p.setPen(col)
            p.drawText(QRectF(0, 0, 24, 24), Qt.AlignCenter, "1")
    elif name == "playlist":
        line((4, 6), (20, 6))
        line((4, 12), (13, 12))
        line((4, 18), (13, 18))
        poly((16, 11), (21, 15), (16, 19))
    elif name == "folder":
        poly((3, 6), (9, 6), (11.5, 8.5), (21, 8.5), (21, 19), (3, 19))
    elif name == "plus_folder":
        poly((3, 6), (9, 6), (11.5, 8.5), (21, 8.5), (21, 19), (3, 19))
        p.setCompositionMode(QPainter.CompositionMode_Clear)
        p.setPen(QPen(Qt.transparent, 2, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(12, 11.5), QPointF(12, 16.5))
        p.drawLine(QPointF(9.5, 14), QPointF(14.5, 14))
    elif name == "cc":
        p.setPen(QPen(col, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(QRectF(3, 5, 18, 14), 3.5, 3.5)
        p.drawArc(QRectF(6.5, 9.2, 4.6, 5.6), 45 * 16, 270 * 16)
        p.drawArc(QRectF(13, 9.2, 4.6, 5.6), 45 * 16, 270 * 16)
    elif name == "pin":
        poly((9, 3), (15, 3), (14, 10), (18, 14), (6, 14), (10, 10))
        line((12, 14), (12, 21))

    p.end()
    return QIcon(pm)


# ---------------------------------------------------------------- widgets
class ClickSlider(QSlider):
    """Slider that jumps to the clicked position instead of paging."""

    def __init__(self, *args):
        super().__init__(*args)
        self.setPageStep(0)
        self.setFocusPolicy(Qt.NoFocus)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.maximum() > self.minimum():
            value = QStyle.sliderValueFromPosition(
                self.minimum(), self.maximum(), int(event.x()), max(1, self.width())
            )
            self.setValue(value)
            self.sliderMoved.emit(value)
        super().mousePressEvent(event)


class DropPopup(QWidget):
    """Floating panel that closes when you click anywhere else."""

    closed = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.closed_at = 0.0

    def hideEvent(self, event):
        self.closed_at = time.monotonic()
        self.closed.emit()
        super().hideEvent(event)


class FloatingBar(QWidget):
    """Frameless window that holds the control bar above the video in full screen."""

    PAD = 18  # transparent margin so the drop shadow has room

    def __init__(self, parent):
        super().__init__(parent, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        box = QVBoxLayout(self)
        box.setContentsMargins(self.PAD, self.PAD, self.PAD, self.PAD)
        box.setSpacing(0)


class VideoSurface(QVideoWidget):
    clicked = pyqtSignal()
    double_clicked = pyqtSignal()
    moved = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit()

    def mouseMoveEvent(self, event):
        self.moved.emit()


def collect_videos(paths):
    found = []
    for path in paths:
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                dirs.sort()
                found += [os.path.join(root, f) for f in sorted(files) if f.lower().endswith(VIDEO_EXTS)]
        elif os.path.isfile(path) and path.lower().endswith(VIDEO_EXTS):
            found.append(path)
    return found


# ---------------------------------------------------------------- subtitles
TIME_RE = re.compile(
    r"(?:(\d+):)?(\d{1,2}):(\d{2})[,.](\d{1,3})\s*-->\s*(?:(\d+):)?(\d{1,2}):(\d{2})[,.](\d{1,3})"
)


def _ms(h, m, s, frac):
    return ((int(h or 0) * 60 + int(m)) * 60 + int(s)) * 1000 + int(frac.ljust(3, "0")[:3])


def _clean_markup(text):
    """Escape the text, keep <i> <b> <u>, drop every other tag."""
    text = html.escape(text, quote=False)
    text = re.sub(r"&lt;(/?)(i|b|u)&gt;", r"<\1\2>", text, flags=re.I)
    text = re.sub(r"&lt;/?[^&]*?&gt;", "", text)
    return text.replace("\n", "<br>")


def read_text(path):
    with open(path, "rb") as f:
        raw = f.read()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("cp1252", errors="replace")


def parse_srt_vtt(text):
    cues = []
    for block in re.split(r"\r?\n\s*\r?\n", text.replace("\ufeff", "")):
        lines = block.strip().splitlines()
        for i, line in enumerate(lines):
            m = TIME_RE.search(line)
            if m:
                g = m.groups()
                body = "\n".join(lines[i + 1:]).strip()
                if body:
                    cues.append((_ms(*g[0:4]), _ms(*g[4:8]), _clean_markup(body)))
                break
    return cues


def parse_ass(text):
    cues = []
    stamp = re.compile(r"\s*(\d+):(\d{2}):(\d{2})[.](\d{1,3})")
    for line in text.splitlines():
        if not line.startswith("Dialogue:"):
            continue
        parts = line[9:].split(",", 9)
        if len(parts) < 10:
            continue
        a, b = stamp.match(parts[1]), stamp.match(parts[2])
        if not (a and b):
            continue
        body = re.sub(r"\{[^}]*\}", "", parts[9]).replace("\\N", "\n").replace("\\n", "\n").strip()
        if body:
            cues.append((_ms(*a.groups()), _ms(*b.groups()), _clean_markup(body)))
    return cues


def find_subtitle_for(video_path):
    """Look next to the video for a subtitle file with the same name (Movie.srt, Movie.en.srt ...)."""
    folder, name = os.path.split(video_path)
    base = os.path.splitext(name)[0].lower()
    try:
        files = sorted(os.listdir(folder))
    except OSError:
        return None
    for f in files:
        stem, ext = os.path.splitext(f)
        if ext.lower() in SUB_EXTS and (stem.lower() == base or stem.lower().startswith(base + ".")):
            return os.path.join(folder, f)
    return None


# ---------------------------------------------------------------- main window
class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Luma Player")
        self.resize(1180, 740)
        self.setMinimumSize(900, 600)
        self.setAcceptDrops(True)

        self.playlist = []
        self.current_index = -1
        self.repeat_mode = REPEAT_OFF
        self._previous_volume = 65
        self._last_mouse = QPoint()
        self.cues = []
        self.cue_starts = []
        self.sub_name = ""
        self.sub_delay = 0
        self.subs_enabled = True
        self.sub_size_idx = 2
        self._shown_cue = UNSET

        self.media_player = QMediaPlayer(self, QMediaPlayer.VideoSurface)
        self.video_widget = VideoSurface()
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setNotifyInterval(100)

        root = QWidget()
        root.setObjectName("root")
        outer = self.outer = QVBoxLayout(root)
        outer.setContentsMargins(16, 12, 16, 10)
        outer.setSpacing(10)

        self.header = self._build_header()
        outer.addWidget(self.header)

        outer.addWidget(self._build_video_area(), 1)
        self.playlist_popup = self._build_playlist_popup()

        self.bottom = self._build_controls()
        self.bottom_wrap = QWidget()
        wrap_layout = QHBoxLayout(self.bottom_wrap)
        wrap_layout.setContentsMargins(0, 0, 0, 0)
        wrap_layout.addWidget(self.bottom)
        outer.addWidget(self.bottom_wrap)
        self.float_bar = FloatingBar(self)

        self.status_bar = QWidget()
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(6, 0, 6, 0)
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status")
        hint = QLabel("Space play   ←/→ seek   ↑/↓ volume   N/P next/previous   C subtitles   F full screen")
        hint.setObjectName("hint")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(hint)
        outer.addWidget(self.status_bar)
        self.setCentralWidget(root)

        # fullscreen auto-hide
        self.fs_timer = QTimer(self)
        self.fs_timer.setSingleShot(True)
        self.fs_timer.setInterval(2500)
        self.fs_timer.timeout.connect(self.hide_fs_controls)
        self.mouse_poll = QTimer(self)
        self.mouse_poll.setInterval(80)
        self.mouse_poll.timeout.connect(self.poll_mouse)
        self.click_timer = QTimer(self)
        self.click_timer.setSingleShot(True)
        self.click_timer.setInterval(220)
        self.click_timer.timeout.connect(self.toggle_playback)
        self.video_widget.clicked.connect(self.click_timer.start)
        self.video_widget.double_clicked.connect(self._video_double_click)

        mp = self.media_player
        mp.positionChanged.connect(self.position_changed)
        mp.durationChanged.connect(self.duration_changed)
        mp.stateChanged.connect(self.playback_state_changed)
        mp.mediaStatusChanged.connect(self.media_status_changed)
        mp.error.connect(self.handle_error)

        shortcuts = {
            "Ctrl+O": self.open_file,
            "Ctrl+Shift+O": self.open_folder,
            "Space": self.toggle_playback,
            "F": self.toggle_fullscreen,
            "Escape": self.exit_fullscreen,
            "Left": lambda: self.seek_by(-5000),
            "Right": lambda: self.seek_by(5000),
            "J": lambda: self.seek_by(-10000),
            "K": lambda: self.seek_by(10000),
            "Up": lambda: self.volume_slider.setValue(self.volume_slider.value() + 5),
            "Down": lambda: self.volume_slider.setValue(self.volume_slider.value() - 5),
            "M": self.toggle_mute,
            "C": self.toggle_subtitles,
            "T": self.cycle_theme,
            "Z": lambda: self.change_sub_delay(-100),
            "X": lambda: self.change_sub_delay(100),
            "N": self.next_video,
            "P": self.previous_video,
            "R": self.cycle_repeat,
            "L": self.toggle_playlist,
            "]": lambda: self.change_speed(1),
            "[": lambda: self.change_speed(-1),
        }
        for seq, callback in shortcuts.items():
            sc = QShortcut(QKeySequence(seq), self)
            sc.setContext(Qt.ApplicationShortcut)
            sc.activated.connect(callback)

        self.set_volume(self._previous_volume)
        self.update_playlist_ui()
        self.apply_subtitle_style()
        self.settings = QSettings("LumaPlayer", "Player")
        self.apply_theme(str(self.settings.value("theme", "Normal")), save=False)

    # ------------------------------------------------------------ UI builders
    def _tool_button(self, icon, tooltip, callback, size=(40, 40), text=None):
        button = QPushButton(text or "")
        button.setObjectName("tool")
        button.setFixedSize(*size)
        button.setFocusPolicy(Qt.NoFocus)
        button.setToolTip(tooltip)
        button.setCursor(Qt.PointingHandCursor)
        if icon:
            button.setIcon(make_icon(icon))
            button.setIconSize(QSize(22, 22))
        button.clicked.connect(callback)
        return button

    def _build_header(self):
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(46)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 0, 8, 0)
        layout.setSpacing(8)

        logo = QLabel()
        logo.setObjectName("logo")
        logo.setFixedSize(26, 26)
        logo.setAlignment(Qt.AlignCenter)
        self.logo = logo
        layout.addWidget(logo)
        brand = QLabel("Luma Player")
        brand.setObjectName("brand")
        layout.addWidget(brand)

        self.now_playing = QLabel("Nothing playing")
        self.now_playing.setObjectName("muted")
        self.now_playing.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.now_playing.setContentsMargins(10, 0, 0, 0)
        layout.addWidget(self.now_playing, 1)

        # two theme options, shown as one segmented switch
        self.theme_buttons = {}
        self.theme_group = QButtonGroup(self)
        switch = QHBoxLayout()
        switch.setSpacing(0)
        for name, obj in (("Normal", "seg_l"), ("Japanese", "seg_r")):
            button = QPushButton(name)
            button.setObjectName(obj)
            button.setCheckable(True)
            button.setFixedHeight(30)
            button.setFocusPolicy(Qt.NoFocus)
            button.setToolTip(f"{name} theme (T switches theme)")
            button.clicked.connect(lambda _=False, n=name: self.apply_theme(n))
            self.theme_group.addButton(button)
            self.theme_buttons[name] = button
            switch.addWidget(button)
        layout.addLayout(switch)

        self.playlist_button = QPushButton("Playlist  ▾")
        self.playlist_button.setIcon(make_icon("playlist"))
        self.playlist_button.setIconSize(QSize(16, 16))
        self.playlist_button.setCheckable(True)
        self.playlist_button.setFixedHeight(30)
        self.playlist_button.setStyleSheet("padding: 0 12px;")
        self.playlist_button.setFocusPolicy(Qt.NoFocus)
        self.playlist_button.setToolTip("Show the playlist (L)")
        self.playlist_button.clicked.connect(self.toggle_playlist)
        layout.addWidget(self.playlist_button)

        folder_button = QPushButton()
        folder_button.setObjectName("tool")
        folder_button.setFixedSize(32, 32)
        folder_button.setIcon(make_icon("plus_folder"))
        folder_button.setIconSize(QSize(18, 18))
        folder_button.setFocusPolicy(Qt.NoFocus)
        folder_button.setToolTip("Add a folder of videos (Ctrl+Shift+O)")
        folder_button.clicked.connect(self.open_folder)
        self.folder_button = folder_button
        layout.addWidget(folder_button)

        self.pin_button = QPushButton()
        self.pin_button.setObjectName("tool")
        self.pin_button.setFixedSize(32, 32)
        self.pin_button.setIcon(make_icon("pin", C["muted"]))
        self.pin_button.setIconSize(QSize(18, 18))
        self.pin_button.setCheckable(True)
        self.pin_button.setFocusPolicy(Qt.NoFocus)
        self.pin_button.setToolTip("Keep this window above other windows")
        self.pin_button.toggled.connect(self.toggle_on_top)
        layout.addWidget(self.pin_button)

        self.open_button = QPushButton("  Open videos")
        self.open_button.setObjectName("primary")
        self.open_button.setIcon(make_icon("folder", C["ink"]))
        self.open_button.setIconSize(QSize(16, 16))
        self.open_button.setFixedHeight(30)
        self.open_button.setStyleSheet("padding: 0 14px;")
        self.open_button.setFocusPolicy(Qt.NoFocus)
        self.open_button.setToolTip("Choose one or more video files (Ctrl+O)")
        self.open_button.clicked.connect(self.open_file)
        layout.addWidget(self.open_button)
        return header

    def _build_video_area(self):
        frame = QFrame()
        frame.setObjectName("videoframe")
        self.video_frame = frame
        box = QVBoxLayout(frame)
        box.setContentsMargins(2, 2, 2, 2)
        box.setSpacing(0)
        holder = QWidget()
        self.video_stack = QStackedLayout(holder)
        self.video_stack.setContentsMargins(0, 0, 0, 0)
        self.empty_state = QLabel()
        self.empty_state.setObjectName("stage_empty")
        self.empty_state.setAlignment(Qt.AlignCenter)
        self.video_stack.addWidget(self.empty_state)
        self.video_stack.addWidget(self.video_widget)
        self.video_stack.setCurrentWidget(self.empty_state)
        box.addWidget(holder, 1)
        # subtitles sit in a strip under the picture: always visible on every video backend
        self.sub_label = QLabel()
        self.sub_label.setObjectName("subs")
        self.sub_label.setAlignment(Qt.AlignCenter)
        self.sub_label.setWordWrap(True)
        self.sub_label.setTextFormat(Qt.RichText)
        self.sub_label.hide()
        box.addWidget(self.sub_label)
        return frame

    def _build_playlist_popup(self):
        popup = DropPopup(self)
        popup.closed.connect(lambda: self.playlist_button.setChecked(False))
        shell = QVBoxLayout(popup)
        shell.setContentsMargins(0, 0, 0, 0)
        frame = QFrame()
        frame.setObjectName("dropdown")
        shell.addWidget(frame)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 10)
        layout.setSpacing(8)

        top = QHBoxLayout()
        title = QLabel("Playlist")
        title.setObjectName("panel_title")
        self.count_label = QLabel("0 videos")
        self.count_label.setObjectName("count")
        top.addWidget(title)
        top.addStretch()
        top.addWidget(self.count_label)
        layout.addLayout(top)

        self.list_widget = QListWidget()
        self.list_widget.setFocusPolicy(Qt.NoFocus)
        self.list_widget.itemClicked.connect(lambda item: self.play_from_list(self.list_widget.row(item)))
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.playlist_context_menu)
        layout.addWidget(self.list_widget, 1)

        self.list_empty = QLabel("Videos you open appear here.")
        self.list_empty.setObjectName("empty")
        self.list_empty.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.list_empty, 1)

        footer = QHBoxLayout()
        hint = QLabel("Right-click a video to remove it")
        hint.setObjectName("hint")
        clear = QPushButton("Clear all")
        clear.setFocusPolicy(Qt.NoFocus)
        clear.setFixedHeight(28)
        clear.setStyleSheet("padding: 0 12px;")
        clear.clicked.connect(self.clear_playlist)
        footer.addWidget(hint)
        footer.addStretch()
        footer.addWidget(clear)
        layout.addLayout(footer)
        return popup

    def _build_controls(self):
        bottom = QFrame()
        bottom.setObjectName("bottom")
        layout = self.bottom_layout = QVBoxLayout(bottom)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(6)

        timeline = QHBoxLayout()
        timeline.setSpacing(12)
        self.current_time = QLabel("00:00")
        self.current_time.setObjectName("time")
        self.current_time.setMinimumWidth(48)
        self.current_time.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.position_slider = ClickSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.setToolTip("Seek")
        self.position_slider.sliderMoved.connect(self.set_position)
        self.duration_time = QLabel("00:00")
        self.duration_time.setObjectName("time")
        self.duration_time.setMinimumWidth(48)
        timeline.addWidget(self.current_time)
        timeline.addWidget(self.position_slider, 1)
        timeline.addWidget(self.duration_time)
        layout.addLayout(timeline)

        row = QHBoxLayout()
        row.setSpacing(6)
        self.prev_button = self._tool_button("prev", "Previous video (P)", self.previous_video)
        row.addWidget(self.prev_button)
        self.skip_back = self._tool_button(None, "Back 10 seconds (J)", lambda: self.seek_by(-10000), (52, 40), "−10s")
        row.addWidget(self.skip_back)
        self.play_button = QPushButton()
        self.play_button.setObjectName("play")
        self.play_button.setFixedSize(56, 56)
        self.play_button.setIcon(make_icon("play", C["ink"]))
        self.play_button.setIconSize(QSize(26, 26))
        self.play_button.setFocusPolicy(Qt.NoFocus)
        self.play_button.setCursor(Qt.PointingHandCursor)
        self.play_button.setToolTip("Play or pause (Space)")
        self.play_button.clicked.connect(self.toggle_playback)
        row.addWidget(self.play_button)
        self.skip_fwd = self._tool_button(None, "Forward 10 seconds (K)", lambda: self.seek_by(10000), (52, 40), "+10s")
        row.addWidget(self.skip_fwd)
        self.next_button = self._tool_button("next", "Next video (N)", self.next_video)
        row.addWidget(self.next_button)
        self.stop_button = self._tool_button("stop", "Stop", self.stop_playback)
        row.addWidget(self.stop_button)
        row.addStretch()

        self.speed_box = QComboBox()
        self.speed_box.setFocusPolicy(Qt.NoFocus)
        self.speed_box.setToolTip("Playback speed ([ and ])")
        for s in SPEEDS:
            self.speed_box.addItem(f"{s:g}×")
        self.speed_box.setCurrentIndex(SPEEDS.index(1.0))
        self.speed_box.currentIndexChanged.connect(self.set_speed)
        row.addWidget(self.speed_box)

        self.repeat_button = self._tool_button("repeat", "Repeat: off (R)", self.cycle_repeat)
        row.addWidget(self.repeat_button)
        self.subtitle_button = self._tool_button("cc", "Subtitles (C)", self.show_subtitle_menu)
        row.addWidget(self.subtitle_button)
        row.addSpacing(10)

        self.volume_button = self._tool_button("volume", "Mute or restore volume (M)", self.toggle_mute)
        row.addWidget(self.volume_button)
        self.volume_slider = ClickSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self._previous_volume)
        self.volume_slider.setFixedWidth(110)
        self.volume_slider.setToolTip("Volume (↑ and ↓)")
        self.volume_slider.valueChanged.connect(self.set_volume)
        row.addWidget(self.volume_slider)
        self.volume_value = QLabel("65%")
        self.volume_value.setObjectName("time")
        self.volume_value.setMinimumWidth(40)
        row.addWidget(self.volume_value)
        row.addSpacing(10)

        self.fullscreen_button = self._tool_button("fullscreen", "Full screen (F)", self.toggle_fullscreen)
        row.addWidget(self.fullscreen_button)
        layout.addLayout(row)
        # hidden in the small full screen bar
        self.compact_hidden = [
            self.skip_back, self.skip_fwd, self.stop_button, self.speed_box,
            self.repeat_button, self.volume_value,
        ]
        return bottom

    # ------------------------------------------------------------ opening media
    def open_file(self):
        filenames, _ = QFileDialog.getOpenFileNames(
            self,
            "Open videos",
            "",
            "Video files (*.mp4 *.mkv *.avi *.mov *.wmv *.m4v *.webm *.flv *.mpg *.mpeg);;All files (*)",
        )
        if filenames:
            self.clear_playlist()
            self.add_files(filenames, play_first=True)

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Add a folder of videos")
        if not folder:
            return
        videos = collect_videos([folder])
        if not videos:
            self.status_label.setText("No supported videos found in that folder")
            return
        self.add_files(videos, play_first=self.current_index == -1)

    def add_files(self, paths, play_first):
        first_new = len(self.playlist)
        for path in paths:
            path = os.path.abspath(path)
            self.playlist.append(path)
            item = QListWidgetItem(os.path.basename(path))
            item.setToolTip(path)
            self.list_widget.addItem(item)
        self.update_playlist_ui()
        if play_first and len(self.playlist) > first_new:
            self.play_index(first_new)

    def play_index(self, index):
        if not 0 <= index < len(self.playlist):
            return
        self.current_index = index
        path = self.playlist[index]
        name = os.path.basename(path)
        self.media_player.stop()
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
        self.media_player.setPlaybackRate(SPEEDS[self.speed_box.currentIndex()])
        self.video_stack.setCurrentWidget(self.video_widget)
        self.setWindowTitle(f"{name} - Luma Player")
        self.now_playing.setText(name)
        self.status_label.setText(f"Loading {name}")
        self.clear_subtitles()
        found = find_subtitle_for(path)
        if found:
            self.load_subtitles(found)
        self.refresh_highlight()
        self.list_widget.setCurrentRow(index)
        self.media_player.play()

    def play_from_list(self, row):
        self.playlist_popup.hide()
        self.play_index(row)

    def playlist_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if item is None:
            return
        row = self.list_widget.row(item)
        menu = QMenu(self.playlist_popup)
        menu.addAction("Play", lambda: self.play_from_list(row))
        menu.addAction("Remove from playlist", lambda: self.remove_at(row))
        menu.exec_(self.list_widget.viewport().mapToGlobal(pos))

    def remove_at(self, row):
        if not 0 <= row < len(self.playlist):
            return
        if row == self.current_index:
            self.reset_player()
        elif row < self.current_index:
            self.current_index -= 1
        self.list_widget.takeItem(row)
        del self.playlist[row]
        self.update_playlist_ui()

    def clear_playlist(self):
        self.reset_player()
        self.list_widget.clear()
        self.playlist.clear()
        self.update_playlist_ui()

    def reset_player(self):
        self.media_player.stop()
        self.media_player.setMedia(QMediaContent())
        self.current_index = -1
        self.clear_subtitles()
        self.video_stack.setCurrentWidget(self.empty_state)
        self.setWindowTitle("Luma Player")
        self.now_playing.setText("Nothing playing")
        self.status_label.setText("Ready")

    def update_playlist_ui(self):
        n = len(self.playlist)
        self.count_label.setText(f"{n} video{'s' if n != 1 else ''}")
        self.playlist_button.setText(f"Playlist ({n})  ▾" if n else "Playlist  ▾")
        self.list_widget.setVisible(n > 0)
        self.list_empty.setVisible(n == 0)
        self.refresh_highlight()

    def refresh_highlight(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            active = i == self.current_index
            font = item.font()
            font.setBold(active)
            item.setFont(font)
            item.setForeground(QColor(C["accent"] if active else C["text"]))

    # drag and drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        paths = [u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()]
        videos = collect_videos(paths)
        subs = [p for p in paths if p.lower().endswith(SUB_EXTS)]
        if videos:
            self.add_files(videos, play_first=True)
        if subs:
            if self.current_index != -1:
                self.load_subtitles(subs[0])
            else:
                self.status_label.setText("Open a video first, then add its subtitles")
        elif not videos:
            self.status_label.setText("Those files are not supported video or subtitle formats")

    # ------------------------------------------------------------ playback
    def toggle_playback(self):
        if self.media_player.mediaStatus() == QMediaPlayer.NoMedia:
            if self.playlist:
                self.play_index(max(self.current_index, 0))
            else:
                self.open_file()
            return
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def stop_playback(self):
        self.media_player.stop()

    def next_video(self):
        if not self.playlist:
            return
        index = self.current_index + 1
        if index >= len(self.playlist):
            if self.repeat_mode != REPEAT_ALL:
                self.status_label.setText("End of playlist")
                return
            index = 0
        self.play_index(index)

    def previous_video(self):
        if not self.playlist:
            return
        if self.media_player.position() > 3000 or self.current_index <= 0:
            self.set_position(0)
        else:
            self.play_index(self.current_index - 1)

    def cycle_repeat(self):
        self.repeat_mode = (self.repeat_mode + 1) % 3
        name = {REPEAT_OFF: "repeat", REPEAT_ALL: "repeat", REPEAT_ONE: "repeat_one"}[self.repeat_mode]
        color = C["text"] if self.repeat_mode == REPEAT_OFF else C["accent"]
        self.repeat_button.setIcon(make_icon(name, color))
        label = REPEAT_NAMES[self.repeat_mode]
        self.repeat_button.setToolTip(f"Repeat: {label} (R)")
        self.status_label.setText(f"Repeat: {label}")

    def set_speed(self, index):
        rate = SPEEDS[index]
        self.media_player.setPlaybackRate(rate)
        self.status_label.setText(f"Speed: {rate:g}×")

    def change_speed(self, step):
        i = max(0, min(self.speed_box.currentIndex() + step, len(SPEEDS) - 1))
        self.speed_box.setCurrentIndex(i)

    def set_position(self, position):
        self.media_player.setPosition(position)
        self.current_time.setText(self.format_time(position))
        self.update_subtitle(position)

    def seek_by(self, amount):
        target = max(0, min(self.media_player.position() + amount, self.media_player.duration()))
        self.set_position(target)

    def position_changed(self, position):
        if not self.position_slider.isSliderDown():
            self.position_slider.setValue(position)
        self.current_time.setText(self.format_time(position))
        self.update_subtitle(position)

    def duration_changed(self, duration):
        self.position_slider.setRange(0, duration)
        self.duration_time.setText(self.format_time(duration))

    def playback_state_changed(self, state):
        playing = state == QMediaPlayer.PlayingState
        self.play_button.setIcon(make_icon("pause" if playing else "play", C["ink"]))
        if playing:
            self.status_label.setText("Now playing")
            if self.isFullScreen():
                self.fs_timer.start()
        elif state == QMediaPlayer.PausedState:
            self.status_label.setText("Paused")
        elif state == QMediaPlayer.StoppedState and self.current_index != -1:
            self.status_label.setText("Stopped")

    def media_status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            if self.repeat_mode == REPEAT_ONE:
                self.set_position(0)
                self.media_player.play()
            elif self.current_index + 1 < len(self.playlist) or (self.repeat_mode == REPEAT_ALL and self.playlist):
                self.next_video()
            else:
                self.status_label.setText("Playback finished")
        elif status == QMediaPlayer.InvalidMedia:
            self.video_stack.setCurrentWidget(self.empty_state)
            self.status_label.setText("This video could not be opened. Try another file.")

    def handle_error(self, error):
        message = self.media_player.errorString() or f"Error code {error}"
        self.status_label.setText(f"Playback error: {message}")

    # ------------------------------------------------------------ themes
    def apply_theme(self, name, save=True):
        if name not in THEMES:
            name = "Normal"
        self.theme_name = name
        C.update(THEMES[name])
        self.setStyleSheet(build_style())
        self.refresh_icons()
        self.set_empty_text()
        self.refresh_highlight()
        self.theme_buttons[name].setChecked(True)
        if save:
            self.settings.setValue("theme", name)
            self.status_label.setText(f"{name} theme")

    def cycle_theme(self):
        names = list(THEMES)
        self.apply_theme(names[(names.index(self.theme_name) + 1) % len(names)])

    def refresh_icons(self):
        """Icons are drawn in code, so they are redrawn whenever the palette changes."""
        if C.get("seal"):
            self.logo.setText("光")  # a hanko-style seal: the kanji for light
        else:
            self.logo.setPixmap(make_icon("play", C["ink"]).pixmap(14, 14))
        self.playlist_button.setIcon(make_icon("playlist"))
        self.folder_button.setIcon(make_icon("plus_folder"))
        self.pin_button.setIcon(make_icon("pin", C["accent"] if self.pin_button.isChecked() else C["muted"]))
        self.open_button.setIcon(make_icon("folder", C["ink"]))
        self.prev_button.setIcon(make_icon("prev"))
        self.next_button.setIcon(make_icon("next"))
        self.stop_button.setIcon(make_icon("stop"))
        playing = self.media_player.state() == QMediaPlayer.PlayingState
        self.play_button.setIcon(make_icon("pause" if playing else "play", C["ink"]))
        repeat_name = "repeat_one" if self.repeat_mode == REPEAT_ONE else "repeat"
        repeat_color = C["text"] if self.repeat_mode == REPEAT_OFF else C["accent"]
        self.repeat_button.setIcon(make_icon(repeat_name, repeat_color))
        self.volume_button.setIcon(make_icon("mute" if self.volume_slider.value() == 0 else "volume"))
        self.fullscreen_button.setIcon(make_icon("exit_fullscreen" if self.isFullScreen() else "fullscreen"))
        self.refresh_subtitle_view()

    def set_empty_text(self):
        extra = ""
        if C.get("seal"):
            extra = (
                "<br><br><span style='font-family:\"Yu Mincho\",\"Hiragino Mincho ProN\",\"Noto Serif JP\",serif;"
                " font-size:16px; color:#d9cfb8'>ここに動画をドロップ</span>"
            )
        self.empty_state.setText(
            "<div style='text-align:center'>"
            "<span style='font-size:22px; font-weight:600; color:#ece9e2'>Drop videos here</span><br><br>"
            "<span style='color:#a9a49a'>or press Ctrl+O to choose files</span>"
            + extra + "</div>"
        )

    # ------------------------------------------------------------ subtitles
    def load_subtitle_dialog(self):
        if self.current_index == -1:
            self.status_label.setText("Open a video first, then add its subtitles")
            return
        start = os.path.dirname(self.playlist[self.current_index])
        path, _ = QFileDialog.getOpenFileName(
            self, "Load subtitles", start,
            "Subtitle files (*.srt *.vtt *.ass *.ssa);;All files (*)",
        )
        if path:
            self.load_subtitles(path)

    def load_subtitles(self, path):
        try:
            text = read_text(path)
            cues = parse_ass(text) if path.lower().endswith((".ass", ".ssa")) else parse_srt_vtt(text)
        except OSError as exc:
            self.status_label.setText(f"Could not open subtitles: {exc.strerror or exc}")
            return False
        if not cues:
            self.status_label.setText("No subtitle lines found in that file. Use .srt, .vtt or .ass.")
            return False
        cues.sort(key=lambda c: c[0])
        self.cues = cues
        self.cue_starts = [c[0] for c in cues]
        self.sub_name = os.path.basename(path)
        self.sub_delay = 0
        self.subs_enabled = True
        self._shown_cue = UNSET
        self.refresh_subtitle_view()
        self.update_subtitle(self.media_player.position())
        self.status_label.setText(f"Subtitles loaded: {self.sub_name}")
        return True

    def clear_subtitles(self):
        self.cues, self.cue_starts = [], []
        self.sub_name = ""
        self.sub_delay = 0
        self._shown_cue = UNSET
        self.sub_label.setText("")
        self.refresh_subtitle_view()

    def toggle_subtitles(self):
        if not self.cues:
            self.load_subtitle_dialog()
            return
        self.subs_enabled = not self.subs_enabled
        self._shown_cue = UNSET
        self.refresh_subtitle_view()
        self.update_subtitle(self.media_player.position())
        self.status_label.setText("Subtitles on" if self.subs_enabled else "Subtitles off")

    def change_sub_delay(self, delta):
        if not self.cues:
            return
        self.sub_delay += delta
        self._shown_cue = UNSET
        self.update_subtitle(self.media_player.position())
        self.status_label.setText(f"Subtitle delay: {self.sub_delay / 1000:+.1f} s")

    def change_sub_size(self, step):
        self.sub_size_idx = max(0, min(self.sub_size_idx + step, len(SUB_SIZES) - 1))
        self.apply_subtitle_style()

    def update_subtitle(self, position):
        if not self.cues or not self.subs_enabled:
            return
        t = position - self.sub_delay
        i = bisect.bisect_right(self.cue_starts, t) - 1
        found = None
        for j in (i, i - 1):  # second check covers a long line that overlaps a short one
            if j >= 0 and self.cues[j][0] <= t < self.cues[j][1]:
                found = j
                break
        if found != self._shown_cue:
            self._shown_cue = found
            self.sub_label.setText(self.cues[found][2] if found is not None else "")

    def refresh_subtitle_view(self):
        active = bool(self.cues) and self.subs_enabled
        self.sub_label.setVisible(active)
        self.subtitle_button.setIcon(make_icon("cc", C["accent"] if active else C["text"]))

    def apply_subtitle_style(self):
        size = int(SUB_SIZES[self.sub_size_idx] * (1.5 if self.isFullScreen() else 1))
        self.sub_label.setStyleSheet(
            f"QLabel#subs {{ color: #fffdf5; font-size: {size}px; font-weight: 600; padding: 4px 24px 10px 24px; }}"
        )
        self.sub_label.setFixedHeight(int(size * 2.9) + 14)  # fixed, so the picture never jumps

    def show_subtitle_menu(self):
        menu = QMenu(self)
        has = bool(self.cues)
        title = menu.addAction(self.sub_name or "No subtitles loaded")
        title.setEnabled(False)
        menu.addSeparator()
        menu.addAction("Load subtitle file…", self.load_subtitle_dialog)
        show = menu.addAction("Show subtitles")
        show.setCheckable(True)
        show.setChecked(self.subs_enabled and has)
        show.setEnabled(has)
        show.triggered.connect(lambda: self.toggle_subtitles())
        menu.addSeparator()
        for text, callback in (
            ("Show earlier (−0.5 s)", lambda: self.change_sub_delay(-500)),
            ("Show later (+0.5 s)", lambda: self.change_sub_delay(500)),
            ("Reset timing", lambda: self.change_sub_delay(-self.sub_delay)),
            ("Bigger text", lambda: self.change_sub_size(1)),
            ("Smaller text", lambda: self.change_sub_size(-1)),
        ):
            action = menu.addAction(text, callback)
            action.setEnabled(has)
        menu.addSeparator()
        remove = menu.addAction("Remove subtitles", self.clear_subtitles)
        remove.setEnabled(has)
        # open the menu above the button, since the bar sits at the bottom of the window
        pos = self.subtitle_button.mapToGlobal(QPoint(0, 0))
        menu.exec_(pos - QPoint(0, menu.sizeHint().height() + 6))

    # ------------------------------------------------------------ volume
    def set_volume(self, volume):
        volume = max(0, min(100, volume))
        self.media_player.setVolume(volume)
        self.volume_value.setText(f"{volume}%")
        self.volume_button.setIcon(make_icon("mute" if volume == 0 else "volume"))
        if volume > 0:
            self._previous_volume = volume

    def toggle_mute(self):
        if self.volume_slider.value() == 0:
            self.volume_slider.setValue(self._previous_volume or 65)
        else:
            self.volume_slider.setValue(0)

    # ------------------------------------------------------------ window modes
    def toggle_playlist(self):
        popup = self.playlist_popup
        if popup.isVisible():
            popup.hide()
            return
        if time.monotonic() - popup.closed_at < 0.25:
            # the same click that closed the dropdown also hit the button
            self.playlist_button.setChecked(False)
            return
        popup.setFixedSize(340, min(440, max(220, self.height() - 120)))
        if self.isFullScreen():
            pos = self.mapToGlobal(QPoint(self.width() - popup.width() - 24, 24))
        else:
            button = self.playlist_button
            pos = button.mapToGlobal(QPoint(button.width() - popup.width(), button.height() + 6))
        popup.move(pos)
        popup.show()
        self.playlist_button.setChecked(True)
        if self.current_index >= 0:
            self.list_widget.scrollToItem(self.list_widget.item(self.current_index))

    def toggle_on_top(self, on):
        self.pin_button.setIcon(make_icon("pin", C["accent"] if on else C["muted"]))
        self.setWindowFlag(Qt.WindowStaysOnTopHint, on)
        self.show()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()

    def enter_fullscreen(self):
        # the bar is hidden straight away and only returns when the mouse moves
        for widget in (self.header, self.status_bar, self.bottom_wrap):
            widget.hide()
        self.set_compact(True)
        self.dock_bar(floating=True)
        self.outer.setContentsMargins(0, 0, 0, 0)
        self.outer.setSpacing(0)
        self.video_frame.setStyleSheet("QFrame#videoframe { border: none; border-radius: 0; }")
        self.showFullScreen()
        self._last_mouse = QCursor.pos()
        self.centralWidget().setCursor(Qt.BlankCursor)
        self.mouse_poll.start()
        self.apply_subtitle_style()
        self.fullscreen_button.setIcon(make_icon("exit_fullscreen"))

    def exit_fullscreen(self):
        if not self.isFullScreen():
            return
        self.mouse_poll.stop()
        self.fs_timer.stop()
        self.showNormal()
        self.set_compact(False)
        self.dock_bar(floating=False)
        self.outer.setContentsMargins(16, 12, 16, 10)
        self.outer.setSpacing(10)
        self.video_frame.setStyleSheet("")
        self.centralWidget().unsetCursor()
        for widget in (self.header, self.status_bar, self.bottom_wrap):
            widget.show()
        self.apply_subtitle_style()
        self.fullscreen_button.setIcon(make_icon("fullscreen"))

    def set_compact(self, on):
        """Small control bar for full screen: only the essentials."""
        for widget in self.compact_hidden:
            widget.setVisible(not on)
        size = 44 if on else 56
        self.play_button.setFixedSize(size, size)
        self.play_button.setIconSize(QSize(22, 22) if on else QSize(26, 26))
        self.play_button.setStyleSheet(f"border-radius: {size // 2}px;" if on else "")
        self.bottom_layout.setContentsMargins(*((16, 8, 16, 8) if on else (18, 12, 18, 12)))

    def dock_bar(self, floating):
        """Move the control bar between the window layout and the floating overlay."""
        if floating:
            self.bottom_wrap.layout().removeWidget(self.bottom)
            self.float_bar.layout().addWidget(self.bottom)
            shadow = QGraphicsDropShadowEffect(self.bottom)
            shadow.setBlurRadius(28)
            shadow.setOffset(0, 6)
            shadow.setColor(QColor(0, 0, 0, 170))
            self.bottom.setGraphicsEffect(shadow)
            self.bottom.show()
        else:
            self.float_bar.hide()
            self.float_bar.layout().removeWidget(self.bottom)
            self.bottom.setGraphicsEffect(None)
            self.bottom_wrap.layout().addWidget(self.bottom)
            self.bottom.show()

    def place_float_bar(self):
        """Centre the bar near the bottom of the screen, above the subtitle strip if there is one."""
        pad = FloatingBar.PAD
        bar = self.float_bar
        width = max(320, min(860, self.width() - 40))
        bar.setFixedSize(width + 2 * pad, self.bottom.sizeHint().height() + 2 * pad)
        gap = 28
        if self.sub_label.isVisible():
            gap += self.sub_label.height()
        origin = self.mapToGlobal(QPoint(0, 0))
        x = origin.x() + (self.width() - bar.width()) // 2
        y = origin.y() + self.height() - bar.height() - gap + pad
        bar.move(x, y)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.isFullScreen() and self.float_bar.isVisible():
            self.place_float_bar()

    def _video_double_click(self):
        self.click_timer.stop()
        self.toggle_fullscreen()

    def poll_mouse(self):
        # checks the real cursor position, so it works with any video backend
        pos = QCursor.pos()
        if (pos - self._last_mouse).manhattanLength() < 3:
            return
        self._last_mouse = pos
        self.place_float_bar()
        self.float_bar.show()
        self.centralWidget().unsetCursor()
        self.fs_timer.start()

    def hide_fs_controls(self):
        if not self.isFullScreen():
            return
        if self.bottom.underMouse():  # don't hide while the bar is being used
            self.fs_timer.start()
            return
        self.float_bar.hide()
        self.centralWidget().setCursor(Qt.BlankCursor)

    @staticmethod
    def format_time(milliseconds):
        total_seconds = max(0, milliseconds // 1000)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        return f"{minutes:02}:{seconds:02}"


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    player = VideoPlayer()
    player.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())