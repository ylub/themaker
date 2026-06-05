#!/usr/bin/env python3
import argparse
import colorsys
import json
import plistlib
import re
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path

APP_NAME = "THEMaker"
APP_VERSION = "0.2.0"
APP_AUTHOR = "@ylub"
PROJECT_URL = "https://github.com/ylub/themaker"
COOLORS_URL = "https://coolors.co"
DEFAULT_FG = "F8F8F2"
APP_DIR = Path(__file__).resolve().parent
URL_LOG_FILE = APP_DIR / "used_urls.log"
OUTPUT_DIR = APP_DIR / "colors"
ORIGINAL_PALETTE_KEY = "TheMaker Original Palette"
PALETTE_SOURCE_KEY = "TheMaker Palette Source"
GENERATOR_KEY = "TheMaker Generator"
FAMILY_KEY = "TheMaker Family"
MODE_KEY = "TheMaker Mode"
EXPORT_FORMATS = ("iterm", "kitty", "alacritty", "wezterm", "data")
TERMINAL_ROLE_NAMES = (
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
)
DEFAULT_PREVIEW_LABELS = {
    "normal": "normal text",
    "accent": "accent",
    "warning": "warning",
    "error": "error",
}
ANSI_ROLE_PREVIEW = {
    "red": "error",
    "green": "success/secondary",
    "yellow": "warning",
    "blue": "link/command",
    "magenta": "highlight",
    "cyan": "accent",
}
ANSI_ROLE_SAMPLE_WORDS = {
    "red": "error",
    "green": "success",
    "yellow": "warning",
    "blue": "command",
    "magenta": "highlight",
    "cyan": "accent",
}
ANSI_ROLE_SEED_COLORS = {
    "red": "EF4444",
    "green": "22C55E",
    "yellow": "FACC15",
    "blue": "3B82F6",
    "magenta": "D946EF",
    "cyan": "06B6D4",
}
COMMAND_WORDS = {"back", "quit", "exit", "q", "help", "restart"}

THEME_FAMILIES = [
    {
        "name": "dark",
        "label": "Dark",
        "foreground": DEFAULT_FG,
        "selection": "334155",
        "backgrounds": [
            ("Deep Neutral", "101418"),
            ("Blue Black", "0B0F14"),
            ("Slate Dark", "151A1E"),
            ("Soft Graphite", "1B1F23"),
            ("Warm Dark", "20252B"),
            ("Ink Black", "080A0D"),
            ("Charcoal", "18181B"),
            ("Cool Navy", "0A1020"),
        ],
    },
    {
        "name": "light",
        "label": "Light",
        "foreground": "202124",
        "selection": "DDEBFF",
        "backgrounds": [
            ("Paper White", "FBFAF7"),
            ("Cool White", "F7FAFC"),
            ("Soft Gray", "EEF2F7"),
            ("Warm Canvas", "FFF8ED"),
            ("Pale Mint", "F1FBF6"),
        ],
    },
    {
        "name": "neon",
        "label": "Neon",
        "foreground": "F8FAFC",
        "selection": "22304A",
        "backgrounds": [
            ("Terminal Black", "05070D"),
            ("Electric Navy", "030B1F"),
            ("Violet Black", "11041F"),
            ("Cyber Graphite", "0B1117"),
            ("Night Arcade", "070014"),
        ],
    },
    {
        "name": "pastel",
        "label": "Pastel",
        "foreground": "34313D",
        "selection": "E8DDF7",
        "backgrounds": [
            ("Milk Glass", "FFFDF8"),
            ("Blush Mist", "FFF4F6"),
            ("Lavender Wash", "F6F1FF"),
            ("Mint Cream", "F1FFF8"),
            ("Powder Blue", "F1F8FF"),
        ],
    },
    {
        "name": "high contrast",
        "label": "High Contrast",
        "foreground": "FFFFFF",
        "selection": "444444",
        "backgrounds": [
            ("Pure Black", "000000"),
            ("Near Black", "050505"),
            ("Ink", "090909"),
            ("White", "FFFFFF"),
            ("Signal Yellow", "FFF200"),
        ],
    },
    {
        "name": "soft",
        "label": "Soft",
        "foreground": "ECEFF4",
        "selection": "3B4252",
        "backgrounds": [
            ("Nord Night", "2E3440"),
            ("Soft Slate", "26313D"),
            ("Muted Teal", "1E3335"),
            ("Dusty Plum", "332A36"),
            ("Quiet Graphite", "252A2E"),
        ],
    },
    {
        "name": "warm",
        "label": "Warm",
        "foreground": "FFF7ED",
        "selection": "4A3428",
        "backgrounds": [
            ("Espresso", "17100D"),
            ("Roasted Umber", "241713"),
            ("Deep Clay", "2B1714"),
            ("Warm Charcoal", "211C18"),
            ("Candlelight", "FFF4E3"),
        ],
    },
    {
        "name": "cool",
        "label": "Cool",
        "foreground": "EAF6FF",
        "selection": "203A4A",
        "backgrounds": [
            ("Arctic Navy", "061723"),
            ("Deep Teal", "062022"),
            ("Steel Blue", "132334"),
            ("Blue Graphite", "111827"),
            ("Ice", "F0FAFF"),
        ],
    },
]


SPLASH = r"""
 _______ _    _ ______ __  __       _
|__   __| |  | |  ____|  \/  |     | |
   | |  | |__| | |__  | \  / | __ _| | _____ _ __
   | |  |  __  |  __| | |\/| |/ _` | |/ / _ \ '__|
   | |  | |  | | |____| |  | | (_| |   <  __/ |
   |_|  |_|  |_|______|_|  |_|\__,_|_|\_\___|_|
"""


def about_text():
    return "\n".join(
        [
            f"{APP_NAME} {APP_VERSION}",
            "Terminal color themes from Coolors palettes or hex colors.",
            f"Created by {APP_AUTHOR} on GitHub.",
            f"Project: {PROJECT_URL}",
            "Built with help from Codex.",
            f"Inspired by palette ideas from Coolors: {COOLORS_URL}",
        ]
    )


def show_splash(wait=False):
    print(SPLASH.strip("\n"))
    print(about_text())
    if wait:
        input("\nPress Enter to start.")
    print()


def clean_hex(h):
    h = h.strip().lstrip("#")
    if re.fullmatch(r"[0-9a-fA-F]{4}", h):
        return "".join(channel * 2 for channel in h[:3]).upper()
    if re.fullmatch(r"[0-9a-fA-F]{8}", h):
        return h[:6].upper()
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        raise ValueError(f"Invalid hex color: {h}")
    return h.upper()


def hex_to_rgb(hex_color):
    h = clean_hex(hex_color)
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "".join(f"{max(0, min(255, value)):02X}" for value in rgb)


def rgb_plist(hex_color):
    r, g, b = hex_to_rgb(hex_color)
    return {
        "Red Component": r / 255,
        "Green Component": g / 255,
        "Blue Component": b / 255,
        "Alpha Component": 1.0,
        "Color Space": "sRGB",
    }


def plist_rgb_to_hex(value):
    return rgb_to_hex(
        tuple(
            round(value.get(component, 0) * 255)
            for component in (
                "Red Component",
                "Green Component",
                "Blue Component",
            )
        )
    )


def parse_palette_input(value):
    raw_value = value.strip()
    parsed_url = urlparse(raw_value)
    palette_text = (
        parsed_url.path.rstrip("/").split("/")[-1]
        if parsed_url.scheme or parsed_url.netloc
        else raw_value
    )
    palette_text = palette_text.replace("-", " ").replace(",", " ")
    colors = [clean_hex(part) for part in palette_text.split()]

    if len(colors) < 5:
        raise ValueError("Palette should contain at least 5 hex colors.")

    return colors


def ansi_swatch(hex_color, text="  "):
    r, g, b = hex_to_rgb(hex_color)
    return f"\033[48;2;{r};{g};{b}m{text}\033[0m"


def log_used_url(url, colors):
    URL_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with URL_LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(f"{timestamp}\n")
        handle.write(f"URL: {url.strip()}\n")
        handle.write("Palette:\n")
        for index, color in enumerate(colors, 1):
            handle.write(f"  {index}. #{color} {ansi_swatch(color, '      ')}\n")
        handle.write("\n")


def brightness(hex_color):
    r, g, b = hex_to_rgb(hex_color)
    return r + g + b


def color_distance(first_hex, second_hex):
    first = hex_to_rgb(first_hex)
    second = hex_to_rgb(second_hex)
    return sum((a - b) ** 2 for a, b in zip(first, second)) ** 0.5


def complementary_color(hex_color, family, mode):
    r, g, b = (channel / 255 for channel in hex_to_rgb(hex_color))
    hue, lightness, saturation = colorsys.rgb_to_hls(r, g, b)
    hue = (hue + 0.5) % 1.0

    family_name = family["name"]
    if mode == "bright":
        saturation = max(saturation, 0.75)
        lightness = min(max(lightness, 0.48), 0.68)
    elif mode == "soft":
        saturation *= 0.55
        lightness = min(max(lightness, 0.45), 0.72)

    if family_name == "pastel":
        saturation = min(saturation, 0.42)
        lightness = max(lightness, 0.78)
    elif family_name == "light":
        saturation = min(saturation, 0.65)
        lightness = min(max(lightness, 0.35), 0.58)
    elif family_name in {"neon", "high contrast"}:
        saturation = max(saturation, 0.88)
        lightness = min(max(lightness, 0.52), 0.70)
    else:
        lightness = max(lightness, 0.52)

    rgb = colorsys.hls_to_rgb(hue, lightness, min(saturation, 1.0))
    return rgb_to_hex(tuple(round(channel * 255) for channel in rgb))


def complementary_options(colors, family, mode):
    return unique_color_options(
        (f"Complement of palette {index}", complementary_color(color, family, mode))
        for index, color in enumerate(colors[:5], 1)
    )


def hue_distance(first, second):
    return min(abs(first - second), 1 - abs(first - second))


def hue_for_color(hex_color):
    red, green, blue = hex_to_rgb(hex_color)
    if max(red, green, blue) - min(red, green, blue) < 32:
        return None
    r, g, b = (channel / 255 for channel in (red, green, blue))
    hue, _lightness, saturation = colorsys.rgb_to_hls(r, g, b)
    return None if saturation < 0.12 else hue


def tune_suggested_color(hex_color, family, mode):
    r, g, b = (channel / 255 for channel in hex_to_rgb(hex_color))
    hue, lightness, saturation = colorsys.rgb_to_hls(r, g, b)
    family_name = family["name"]

    if family_name == "pastel":
        saturation = min(max(saturation, 0.45), 0.62)
        lightness = 0.76 if mode == "bright" else 0.82
    elif family_name == "light":
        saturation = min(max(saturation, 0.58), 0.82)
        lightness = 0.46 if mode == "bright" else 0.42
    elif family_name == "neon":
        saturation = max(saturation, 0.92)
        lightness = 0.62
    elif family_name == "high contrast":
        saturation = max(saturation, 0.95)
        lightness = 0.58
    else:
        saturation = min(max(saturation, 0.72), 0.92)
        lightness = 0.64 if mode == "bright" else 0.58

    rgb = colorsys.hls_to_rgb(hue, lightness, min(saturation, 1.0))
    return rgb_to_hex(tuple(round(channel * 255) for channel in rgb))


def shifted_palette_color(hex_color, shift, family, mode):
    r, g, b = (channel / 255 for channel in hex_to_rgb(hex_color))
    hue, _lightness, saturation = colorsys.rgb_to_hls(r, g, b)
    if saturation < 0.12:
        return clean_hex(hex_color)
    hue = (hue + shift) % 1.0
    rgb = colorsys.hls_to_rgb(hue, 0.58, max(saturation, 0.72))
    return tune_suggested_color(
        rgb_to_hex(tuple(round(channel * 255) for channel in rgb)),
        family,
        mode,
    )


def ansi_named_color_options(colors, family, mode):
    palette_hues = [
        hue for color in colors[:5] if (hue := hue_for_color(color)) is not None
    ]
    options = []
    for role, seed_color in ANSI_ROLE_SEED_COLORS.items():
        seed_hue = hue_for_color(seed_color)
        palette_has_hue = seed_hue is not None and any(
            hue_distance(seed_hue, palette_hue) <= 0.08 for palette_hue in palette_hues
        )
        note = (
            "palette already has this hue" if palette_has_hue else "fills a missing hue"
        )
        options.append(
            (
                f"ANSI {role} / {ANSI_ROLE_SAMPLE_WORDS[role]} candidate - {note}",
                tune_suggested_color(seed_color, family, mode),
            )
        )
    return unique_color_options(options)


def palette_fit_options(colors, family, mode):
    options = []
    for index, color in enumerate(colors[:5], 1):
        if hue_for_color(color) is None:
            continue
        options.append(
            (
                f"Palette-fit cool accent from palette {index}",
                shifted_palette_color(color, 0.08, family, mode),
            )
        )
        options.append(
            (
                f"Palette-fit warm accent from palette {index}",
                shifted_palette_color(color, -0.08, family, mode),
            )
        )
    return unique_color_options(options)


def extra_color_options(colors, family, mode):
    return unique_color_options(
        ansi_named_color_options(colors, family, mode)
        + complementary_options(colors, family, mode)
        + palette_fit_options(colors, family, mode)
    )


def bright_variant_color(hex_color, family):
    red, green, blue = hex_to_rgb(hex_color)
    if max(red, green, blue) - min(red, green, blue) < 32:
        return clean_hex(hex_color)

    r, g, b = (channel / 255 for channel in (red, green, blue))
    hue, lightness, saturation = colorsys.rgb_to_hls(r, g, b)
    family_name = family["name"]

    if saturation < 0.08:
        return clean_hex(hex_color)

    original = clean_hex(hex_color)
    saturation = min(max(saturation + 0.16, 0.82), 1.0)
    if family_name == "pastel":
        lightness = 0.74 if lightness > 0.78 else min(lightness + 0.10, 0.78)
        saturation = min(saturation, 0.68)
    elif family_name == "light":
        lightness = 0.48 if lightness > 0.62 else min(lightness + 0.08, 0.62)
    else:
        lightness = 0.66 if lightness > 0.60 else min(lightness + 0.12, 0.68)

    if family_name == "neon":
        saturation = max(saturation, 0.92)
        lightness = 0.64

    rgb = colorsys.hls_to_rgb(hue, lightness, min(saturation, 1.0))
    bright = rgb_to_hex(tuple(round(channel * 255) for channel in rgb))
    if bright == original:
        lightness = min(max(lightness + 0.08, 0.35), 0.72)
        rgb = colorsys.hls_to_rgb(hue, lightness, min(saturation, 1.0))
        bright = rgb_to_hex(tuple(round(channel * 255) for channel in rgb))
    return bright


def ansi_bg(hex_color, text="      "):
    return ansi_swatch(hex_color, text)


def ansi_fg(hex_color, text):
    r, g, b = hex_to_rgb(hex_color)
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"


def ansi_text_on(background, foreground, text):
    bg_r, bg_g, bg_b = hex_to_rgb(background)
    fg_r, fg_g, fg_b = hex_to_rgb(foreground)
    return (
        f"\033[48;2;{bg_r};{bg_g};{bg_b}m"
        f"\033[38;2;{fg_r};{fg_g};{fg_b}m{text}\033[0m"
    )


def preview_palette(colors):
    print("\nPalette:")
    for i, c in enumerate(colors, 1):
        print(f"  {i}. #{c} {ansi_bg(c)} {ansi_fg(c, 'sample text')}")


def palette_as_hex(colors):
    return " ".join(f"#{color}" for color in colors)


def preview_palette_choices(colors):
    print("\nPalette choices:")
    for i, color in enumerate(colors, 1):
        print(f"  {i}. #{color} {ansi_bg(color)} {ansi_fg(color, 'sample text')}")


def preview_extra_color_choices(options):
    print("\nExtra color suggestions:")
    for i, (name, color) in enumerate(options, 1):
        sample_word = "sample text"
        for role, role_word in ANSI_ROLE_SAMPLE_WORDS.items():
            if f"ANSI {role} /" in name:
                sample_word = role_word
                break
        print(
            f"  c{i}. #{color} {ansi_bg(color)} {ansi_fg(color, sample_word)}  {name}"
        )


def color_choice_label(colors, color):
    cleaned = clean_hex(color)
    for index, palette_color in enumerate(colors, 1):
        if cleaned == palette_color:
            return f"palette {index}"
    return "custom"


def preview_families():
    print("\nTheme families:")
    for i, family in enumerate(THEME_FAMILIES, 1):
        print(f"  {i}. {family['label']}")


def preview_backgrounds(family):
    print(f"\nSuggested {family['label'].lower()} backgrounds:")
    for i, (name, color) in enumerate(family["backgrounds"], 1):
        print(f"  {i}. #{color} {ansi_bg(color)} {ansi_bg(color, ' sample ')}  {name}")


def unique_color_options(options):
    seen = set()
    unique = []
    for name, color in options:
        cleaned = clean_hex(color)
        if cleaned in seen:
            continue
        seen.add(cleaned)
        unique.append((name, cleaned))
    return unique


def foreground_options(colors, family, background):
    sorted_colors = sorted(colors, key=brightness)
    darkest, second_darkest = sorted_colors[0], sorted_colors[1]
    second_brightest, brightest = sorted_colors[-2], sorted_colors[-1]
    background_is_light = brightness(background) >= 390

    if background_is_light:
        base_options = [
            ("Family default", family["foreground"]),
            ("Ink", "202124"),
            ("Near black", "111827"),
            ("Palette darkest", darkest),
            ("Palette muted dark", second_darkest),
        ]
    else:
        base_options = [
            ("Family default", family["foreground"]),
            ("Soft white", DEFAULT_FG),
            ("Cool white", "EAF6FF"),
            ("Pure white", "FFFFFF"),
            ("Palette bright", brightest),
            ("Palette soft bright", second_brightest),
        ]

    return unique_color_options(base_options)


def preview_foregrounds(options, background, error_color, labels):
    print("\nSuggested normal text colors:")
    for index, (name, color) in enumerate(options, 1):
        error_note = (
            " close to error" if color_distance(color, error_color) < 90 else ""
        )
        bg_note = (
            " low background contrast" if color_distance(color, background) < 90 else ""
        )
        print(
            f"  {index}. #{color} {ansi_bg(color)} "
            f"{ansi_fg(color, labels['normal'])} "
            f"{ansi_text_on(background, color, labels['normal'])}  {name}{error_note}{bg_note}"
        )


def palette_roles(colors, family):
    sorted_colors = sorted(colors, key=brightness)
    darkest, second_darkest = sorted_colors[0], sorted_colors[1]
    middle = sorted_colors[len(sorted_colors) // 2]
    second_brightest, brightest = sorted_colors[-2], sorted_colors[-1]
    c1, c2, c3, c4, c5 = colors[:5]

    if family["name"] == "light":
        black = family["foreground"]
        cyan = c1
        blue = c1
        bright_black = second_darkest
    elif family["name"] == "high contrast":
        black = "000000"
        cyan = c2
        c3 = "FFF200"
        brightest = c1
        blue = c1
        bright_black = "555555"
    elif family["name"] == "neon":
        black = "030303"
        cyan = c1
        blue = c1
        bright_black = middle
    else:
        black = family["backgrounds"][0][1]
        cyan = c2
        blue = c1
        bright_black = second_brightest

    return {
        "black": black,
        "red": c5,
        "green": brightest if family["name"] in {"high contrast", "neon"} else c1,
        "yellow": c3,
        "blue": blue,
        "magenta": c4,
        "cyan": cyan,
        "white": family["foreground"],
        "bright_black": bright_black,
    }


def preview_theme(colors, background, foreground, roles, labels):
    mapping = [
        ("Background", background, ansi_text_on(background, foreground, " sample ")),
        (
            "Foreground",
            foreground,
            ansi_text_on(background, foreground, labels["normal"]),
        ),
        (
            "Black / ANSI 0 / base",
            roles["black"],
            ansi_text_on(background, roles["black"], "base"),
        ),
        (
            "Red / ANSI 1 / error",
            roles["red"],
            ansi_text_on(background, roles["red"], labels["error"]),
        ),
        (
            "Green / ANSI 2 / success",
            roles["green"],
            ansi_text_on(background, roles["green"], "success"),
        ),
        (
            "Yellow / ANSI 3 / warning",
            roles["yellow"],
            ansi_text_on(background, roles["yellow"], labels["warning"]),
        ),
        (
            "Blue / ANSI 4 / link",
            roles["blue"],
            ansi_text_on(background, roles["blue"], "command"),
        ),
        (
            "Magenta / ANSI 5 / highlight",
            roles["magenta"],
            ansi_text_on(background, roles["magenta"], "highlight"),
        ),
        (
            "Cyan / ANSI 6 / accent",
            roles["cyan"],
            ansi_text_on(background, roles["cyan"], labels["accent"]),
        ),
        ("White / ANSI 7", foreground, ansi_text_on(background, foreground, "normal")),
    ]

    print("\nTheme preview:")
    for label, color, sample in mapping:
        print(f"  {label:<28} #{color} {ansi_bg(color)} {sample}")

    print("\nText preview:")
    print(
        f"  {ansi_text_on(background, foreground, labels['normal'])} (foreground) "
        f"{ansi_text_on(background, roles['cyan'], labels['accent'])} (ANSI 6/cyan/accent) "
        f"{ansi_text_on(background, roles['yellow'], labels['warning'])} (ANSI 3/yellow/warning) "
        f"{ansi_text_on(background, roles['red'], labels['error'])} (ANSI 1/red/error)"
    )

    print("\nANSI example:")
    print(
        f"  {ansi_text_on(background, roles['blue'], '$ themaker export')} "
        f"{ansi_text_on(background, foreground, '--format all')}"
    )
    print(
        f"  {ansi_text_on(background, roles['green'], 'created')} "
        f"{ansi_text_on(background, roles['cyan'], 'theme.itermcolors')} "
        f"{ansi_text_on(background, roles['magenta'], 'theme.lua')}"
    )
    print(
        f"  {ansi_text_on(background, roles['yellow'], 'warning')} "
        f"{ansi_text_on(background, foreground, 'normal text is close to background')}"
    )
    print(
        f"  {ansi_text_on(background, roles['red'], 'error')} "
        f"{ansi_text_on(background, foreground, 'invalid hex color')}"
    )
    if color_distance(foreground, roles["red"]) < 90:
        print("  Warning: normal text is close to the error color.")
    if color_distance(foreground, background) < 90:
        print("  Warning: normal text is close to the background color.")


def make_terminal_colors(colors, background, foreground, mode, family, roles):
    sorted_colors = sorted(colors, key=brightness)

    if mode == "soft":
        ansi8 = sorted_colors[1]
    elif mode == "bright":
        ansi8 = sorted_colors[2]
    else:
        ansi8 = roles["bright_black"]

    return {
        "background": background,
        "foreground": foreground,
        "bold": foreground,
        "cursor": roles["cyan"],
        "cursor_text": background,
        "selection": family["selection"],
        "selected_text": background,
        "ansi": [
            roles["black"],
            roles["red"],
            roles["green"],
            roles["yellow"],
            roles["blue"],
            roles["magenta"],
            roles["cyan"],
            foreground,
        ],
        "bright": [
            ansi8,
            roles["red"],
            roles["green"],
            roles["yellow"],
            roles["blue"],
            roles["magenta"],
            roles["cyan"],
            foreground,
        ],
    }


def make_theme_model(
    colors, background, foreground, mode, family, roles, palette_source="", name=""
):
    return {
        "generator": f"{APP_NAME} {APP_VERSION}",
        "name": name,
        "palette": palette_as_hex(colors),
        "palette_source": palette_source.strip(),
        "family": family["name"],
        "family_label": family["label"],
        "mode": mode,
        "colors": make_terminal_colors(
            colors, background, foreground, mode, family, roles
        ),
    }


def make_theme(colors, background, foreground, mode, family, roles, palette_source=""):
    model = make_theme_model(
        colors, background, foreground, mode, family, roles, palette_source
    )
    terminal_colors = model["colors"]

    theme = {
        "Background Color": rgb_plist(terminal_colors["background"]),
        "Foreground Color": rgb_plist(terminal_colors["foreground"]),
        "Bold Color": rgb_plist(terminal_colors["bold"]),
        "Cursor Color": rgb_plist(terminal_colors["cursor"]),
        "Cursor Text Color": rgb_plist(terminal_colors["cursor_text"]),
        "Selection Color": rgb_plist(terminal_colors["selection"]),
        "Selected Text Color": rgb_plist(terminal_colors["selected_text"]),
    }
    for index, color in enumerate(terminal_colors["ansi"] + terminal_colors["bright"]):
        theme[f"Ansi {index} Color"] = rgb_plist(color)
    theme[ORIGINAL_PALETTE_KEY] = palette_as_hex(colors)
    if palette_source:
        theme[PALETTE_SOURCE_KEY] = palette_source.strip()
    theme[GENERATOR_KEY] = model["generator"]
    theme[FAMILY_KEY] = family["name"]
    theme[MODE_KEY] = mode
    return theme


def format_hex(hex_color):
    return f"#{clean_hex(hex_color)}"


def write_iterm_theme(path, model):
    family = next(item for item in THEME_FAMILIES if item["name"] == model["family"])
    colors = parse_palette_input(model["palette"])
    terminal_colors = model["colors"]
    roles = {
        role: terminal_colors["ansi"][index]
        for index, role in enumerate(TERMINAL_ROLE_NAMES[:-1])
    }
    roles["bright_black"] = terminal_colors["bright"][0]
    theme = make_theme(
        colors,
        terminal_colors["background"],
        terminal_colors["foreground"],
        model["mode"],
        family,
        roles,
        model["palette_source"],
    )
    theme[GENERATOR_KEY] = model["generator"]
    with path.open("wb") as handle:
        plistlib.dump(theme, handle)


def write_kitty_theme(path, model):
    colors = model["colors"]
    lines = [
        f"# Generated by {model['generator']}",
        f"# Palette: {model['palette']}",
        f"foreground {format_hex(colors['foreground'])}",
        f"background {format_hex(colors['background'])}",
        f"cursor {format_hex(colors['cursor'])}",
        f"cursor_text_color {format_hex(colors['cursor_text'])}",
        f"selection_foreground {format_hex(colors['selected_text'])}",
        f"selection_background {format_hex(colors['selection'])}",
        "",
    ]
    for index, color in enumerate(colors["ansi"] + colors["bright"]):
        lines.append(f"color{index} {format_hex(color)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def toml_value(value):
    return json.dumps(value)


def write_alacritty_theme(path, model):
    colors = model["colors"]
    normal = dict(zip(TERMINAL_ROLE_NAMES, colors["ansi"]))
    bright = dict(zip(TERMINAL_ROLE_NAMES, colors["bright"]))
    lines = [
        f"# Generated by {model['generator']}",
        f"# Palette: {model['palette']}",
        "[colors.primary]",
        f"background = {toml_value(format_hex(colors['background']))}",
        f"foreground = {toml_value(format_hex(colors['foreground']))}",
        "",
        "[colors.cursor]",
        f"text = {toml_value(format_hex(colors['cursor_text']))}",
        f"cursor = {toml_value(format_hex(colors['cursor']))}",
        "",
        "[colors.selection]",
        f"text = {toml_value(format_hex(colors['selected_text']))}",
        f"background = {toml_value(format_hex(colors['selection']))}",
        "",
        "[colors.normal]",
    ]
    lines.extend(
        f"{name} = {toml_value(format_hex(color))}" for name, color in normal.items()
    )
    lines.append("")
    lines.append("[colors.bright]")
    lines.extend(
        f"{name} = {toml_value(format_hex(color))}" for name, color in bright.items()
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def lua_string(value):
    return json.dumps(value)


def lua_list(colors):
    return "{ " + ", ".join(lua_string(format_hex(color)) for color in colors) + " }"


def write_wezterm_theme(path, model):
    colors = model["colors"]
    lines = [
        f"-- Generated by {model['generator']}",
        f"-- Palette: {model['palette']}",
        "return {",
        f"  foreground = {lua_string(format_hex(colors['foreground']))},",
        f"  background = {lua_string(format_hex(colors['background']))},",
        f"  cursor_bg = {lua_string(format_hex(colors['cursor']))},",
        f"  cursor_fg = {lua_string(format_hex(colors['cursor_text']))},",
        f"  selection_bg = {lua_string(format_hex(colors['selection']))},",
        f"  selection_fg = {lua_string(format_hex(colors['selected_text']))},",
        f"  ansi = {lua_list(colors['ansi'])},",
        f"  brights = {lua_list(colors['bright'])},",
        "}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_theme_data(path, model):
    path.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")


EXPORTERS = {
    "iterm": (".itermcolors", write_iterm_theme),
    "kitty": (".conf", write_kitty_theme),
    "alacritty": (".toml", write_alacritty_theme),
    "wezterm": (".lua", write_wezterm_theme),
    "data": (".json", write_theme_data),
}


def export_theme_files(model, output_dir, formats, overwrite=False):
    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = safe_filename(model["name"] or "THEMaker Theme")
    written = []
    skipped = []
    for export_format in formats:
        extension, writer = EXPORTERS[export_format]
        out_path = output_dir / f"{base_name}{extension}"
        if out_path.exists() and not overwrite:
            skipped.append(out_path)
            continue
        writer(out_path, model)
        written.append(out_path)
    return written, skipped


def existing_export_paths(model, output_dir, formats):
    base_name = safe_filename(model["name"] or "THEMaker Theme")
    return [
        output_dir / f"{base_name}{EXPORTERS[export_format][0]}"
        for export_format in formats
        if (output_dir / f"{base_name}{EXPORTERS[export_format][0]}").exists()
    ]


def export_theme_files_interactive(model, output_dir, formats):
    existing = existing_export_paths(model, output_dir, formats)
    overwrite = False
    if existing:
        print("\nThese files already exist:")
        for path in existing:
            print(path)
        overwrite = confirm_yes("Overwrite existing files? y/n", default=False)
    return export_theme_files(model, output_dir, formats, overwrite=overwrite)


class WizardBack(Exception):
    pass


class WizardQuit(Exception):
    pass


class WizardRestart(Exception):
    pass


def print_command_help():
    print("\nCommands:")
    print("  help     Show this command list.")
    print("  back     Return to the previous wizard step.")
    print("  restart  Start over from the Coolors URL.")
    print("  quit     Exit without creating a theme.")


def ask(prompt, default=None, allow_back=True):
    while True:
        suffix = f" [{default}]" if default else ""
        try:
            val = input(f"{prompt}{suffix}: ").strip()
        except EOFError:
            raise WizardQuit
        command = val.lower()
        if command in COMMAND_WORDS:
            if command == "help":
                print_command_help()
                continue
            if command in {"quit", "exit", "q"}:
                raise WizardQuit
            if command == "restart":
                raise WizardRestart
            if command == "back":
                if allow_back:
                    raise WizardBack
                print("There is no previous step yet.")
                continue
        return val or (default or "")


def choose_number(prompt, count, default=1):
    raw = ask(prompt, str(default))
    if raw.isdigit():
        n = int(raw)
        if 1 <= n <= count:
            return n
    return default


def choose_foreground(colors, family, background, labels):
    roles = palette_roles(colors, family)
    options = foreground_options(colors, family, background)
    preview_foregrounds(options, background, roles["red"], labels)
    while True:
        raw = ask("Choose normal text color number, or type custom hex", "1").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1][1]
        try:
            return clean_hex(raw)
        except ValueError as error:
            print(error)


def print_role_mapping(colors, roles):
    print("\nANSI role mapping:")
    for role in ("red", "green", "yellow", "blue", "magenta", "cyan"):
        preview_name = ANSI_ROLE_PREVIEW[role]
        sample_word = ANSI_ROLE_SAMPLE_WORDS[role]
        print(
            f"  ANSI {role:<7} / {preview_name:<17} "
            f"#{roles[role]} {ansi_bg(roles[role])} "
            f"{ansi_fg(roles[role], sample_word)} {color_choice_label(colors, roles[role])}"
        )


def choose_role_color(colors, extra_options, role, current_color):
    prompt = (
        f"ANSI {role} color: palette 1-{len(colors)}, suggestion c1-c{len(extra_options)}, "
        "custom hex, or Enter to keep"
    )
    raw = ask(prompt, "").strip()
    if not raw:
        return current_color
    if raw.isdigit() and 1 <= int(raw) <= len(colors):
        return colors[int(raw) - 1]
    if raw.lower().startswith("c") and raw[1:].isdigit():
        index = int(raw[1:])
        if 1 <= index <= len(extra_options):
            return extra_options[index - 1][1]
    try:
        return clean_hex(raw)
    except ValueError as error:
        print(error)
        return choose_role_color(colors, extra_options, role, current_color)


def choose_role_mapping(colors, family, mode, current_roles=None):
    roles = current_roles.copy() if current_roles else palette_roles(colors, family)
    print_role_mapping(colors, roles)
    customize = (
        ask("Change which palette colors feed the ANSI roles? y/n", "n").strip().lower()
    )
    if customize not in {"y", "yes"}:
        return roles

    extra_options = extra_color_options(colors, family, mode)
    print("\nUse palette numbers, extra suggestions, or type a custom hex.")
    preview_palette_choices(colors)
    preview_extra_color_choices(extra_options)
    for role in ("red", "green", "yellow", "blue", "magenta", "cyan"):
        roles[role] = choose_role_color(colors, extra_options, role, roles[role])
    print_role_mapping(colors, roles)
    return roles


def bright_role_suggestions(roles, family):
    return {
        role: bright_variant_color(roles[role], family)
        for role in ("red", "green", "yellow", "blue", "magenta", "cyan")
    }


def offer_bright_ansi_suggestions(roles, family):
    suggestions = bright_role_suggestions(roles, family)
    print("\nBright ANSI suggestions for this same theme:")
    for role in ("red", "green", "yellow", "blue", "magenta", "cyan"):
        current = roles[role]
        suggested = suggestions[role]
        sample_word = ANSI_ROLE_SAMPLE_WORDS[role]
        print(
            f"  {role:<7} #{current} {ansi_bg(current)} {ansi_fg(current, sample_word)}  ->  "
            f"#{suggested} {ansi_bg(suggested)} {ansi_fg(suggested, sample_word)}"
        )

    if not confirm_yes("Apply these bright ANSI suggestions? y/n", default=False):
        return roles

    updated_roles = roles.copy()
    for role, color in suggestions.items():
        updated_roles[role] = color
    updated_roles["bright_black"] = bright_variant_color(roles["bright_black"], family)
    print_role_mapping([], updated_roles)
    return updated_roles


def preview_label_defaults() -> str:
    return " | ".join(
        DEFAULT_PREVIEW_LABELS[key] for key in ("normal", "accent", "warning", "error")
    )


def parse_preview_labels(raw_value: str) -> dict:
    labels = DEFAULT_PREVIEW_LABELS.copy()
    if not raw_value.strip():
        return labels

    parts = [part.strip() for part in raw_value.split("|")]
    if len(parts) == 1:
        parts = [part.strip() for part in raw_value.split(",")]
    if len(parts) != 4 or any(not part for part in parts):
        print("Preview labels need four non-empty labels; keeping defaults.")
        return labels

    for key, value in zip(("normal", "accent", "warning", "error"), parts):
        labels[key] = value
    return labels


def choose_preview_labels() -> dict:
    raw_value = ask(
        "Preview labels: normal | accent | warning | error",
        preview_label_defaults(),
    )
    return parse_preview_labels(raw_value)


def safe_filename(name):
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", name.strip())
    cleaned = cleaned.strip(" .")
    return cleaned or "Coolors Theme"


def confirm_yes(prompt, default=True):
    default_text = "y" if default else "n"
    value = ask(prompt, default_text).strip().lower()
    return value in {"y", "yes"}


def parse_export_formats(raw_value):
    value = raw_value.strip().lower()
    if value == "all":
        return list(EXPORT_FORMATS)
    if value in {"data", "json"}:
        return ["data"]

    aliases = {
        "i": "iterm",
        "iterm2": "iterm",
        "k": "kitty",
        "al": "alacritty",
        "alac": "alacritty",
        "w": "wezterm",
        "wez": "wezterm",
        "d": "data",
        "json": "data",
    }
    normalized = value.replace(",", " ").split()
    formats = []
    for item in normalized:
        export_format = aliases.get(item, item)
        if export_format not in EXPORT_FORMATS:
            raise ValueError(f"Unknown export format: {item}")
        if export_format not in formats:
            formats.append(export_format)
    if not formats:
        raise ValueError("Choose at least one export format.")
    return formats


def choose_export_formats():
    print("\nExport options:")
    print("  all      iTerm2, Kitty, Alacritty, WezTerm, and data JSON")
    print("  one      Choose one format")
    print("  some     Choose a few formats")
    print("  data     Save portable JSON data for someone else to export")
    print("Formats: iterm, kitty, alacritty, wezterm, data")
    while True:
        raw = ask("Export formats", "all")
        if raw.strip().lower() == "one":
            raw = ask("Which one format", "iterm")
        elif raw.strip().lower() == "some":
            raw = ask("Which formats", "iterm kitty")
        try:
            return parse_export_formats(raw)
        except ValueError as error:
            print(error)


def print_export_results(written, skipped):
    if written:
        print("\nCreated:")
        for path in written:
            print(path)
    if skipped:
        print("\nSkipped existing files:")
        for path in skipped:
            print(path)


def list_existing_themes():
    if not OUTPUT_DIR.exists():
        return []
    return sorted(path for path in OUTPUT_DIR.glob("*.itermcolors") if path.is_file())


def choose_existing_theme():
    themes = list_existing_themes()
    if not themes:
        print("\nNo existing themes found in:")
        print(OUTPUT_DIR)
        return None

    print("\nExisting themes:")
    for index, path in enumerate(themes, 1):
        print(f"  {index}. {path.stem}")
    choice = choose_number("Choose theme to edit", len(themes), 1)
    return themes[choice - 1]


def theme_roles(theme):
    return {
        "black": plist_rgb_to_hex(theme["Ansi 0 Color"]),
        "red": plist_rgb_to_hex(theme["Ansi 1 Color"]),
        "green": plist_rgb_to_hex(theme["Ansi 2 Color"]),
        "yellow": plist_rgb_to_hex(theme["Ansi 3 Color"]),
        "blue": plist_rgb_to_hex(theme["Ansi 4 Color"]),
        "magenta": plist_rgb_to_hex(theme["Ansi 5 Color"]),
        "cyan": plist_rgb_to_hex(theme["Ansi 6 Color"]),
        "bright_black": plist_rgb_to_hex(theme["Ansi 8 Color"]),
    }


def theme_palette(theme):
    original = theme.get(ORIGINAL_PALETTE_KEY, "")
    if original:
        return parse_palette_input(original)
    return [
        plist_rgb_to_hex(theme[key])
        for key in (
            "Ansi 2 Color",
            "Ansi 6 Color",
            "Ansi 3 Color",
            "Ansi 5 Color",
            "Ansi 1 Color",
        )
    ]


def load_theme_state(path):
    with path.open("rb") as handle:
        theme = plistlib.load(handle)
    colors = theme_palette(theme)
    print("\nLoaded original palette:")
    preview_palette(colors)
    return {
        "colors": colors,
        "palette_source": theme.get(PALETTE_SOURCE_KEY, path.name),
        "background": plist_rgb_to_hex(theme["Background Color"]),
        "foreground": plist_rgb_to_hex(theme["Foreground Color"]),
        "roles": theme_roles(theme),
        "name": path.stem,
    }


def choose_start_state():
    print("\nStart:")
    print("  1. Create new theme")
    print("  2. Edit existing theme")
    if choose_number("Choose action", 2, 1) == 1:
        return {}, 0

    path = choose_existing_theme()
    if path is None:
        return {}, 0
    return load_theme_state(path), 1


def parallel_theme_suggestions(colors, current_family, current_mode):
    suggestions = []
    preferred = [
        ("bright", "pastel"),
        ("soft", "dark"),
        ("bright", "dark"),
        ("balanced", "light"),
        ("soft", "cool"),
    ]
    seen = {(current_mode, current_family["name"])}
    families = {family["name"]: family for family in THEME_FAMILIES}
    for mode, family_name in preferred:
        if (mode, family_name) in seen or family_name not in families:
            continue
        suggestions.append((mode, families[family_name]))
        seen.add((mode, family_name))
        if len(suggestions) == 3:
            break
    return suggestions


def offer_parallel_themes(
    colors, current_family, current_mode, base_name, output_dir, formats
):
    suggestions = parallel_theme_suggestions(colors, current_family, current_mode)
    if not suggestions:
        return

    print("\nSibling theme ideas from the same palette:")
    for index, (mode, family) in enumerate(suggestions, 1):
        print(f"  {index}. {family['label']} {mode.title()}")

    if not confirm_yes("Create one of these sibling themes too? y/n", default=False):
        return

    choice = choose_number("Choose sibling theme", len(suggestions), 1)
    mode, family = suggestions[choice - 1]
    background = family["backgrounds"][0][1]
    roles = palette_roles(colors, family)
    foreground = foreground_options(colors, family, background)[0][1]
    name = ask("Sibling theme name", f"{base_name} {family['label']} {mode.title()}")
    model = make_theme_model(
        colors,
        background,
        foreground,
        mode,
        family,
        roles,
        palette_as_hex(colors),
        name,
    )
    written, skipped = export_theme_files_interactive(model, output_dir, formats)
    print_export_results(written, skipped)


def run_wizard(initial_state=None, start_stage=None, output_dir=OUTPUT_DIR):
    print(f"\n{APP_NAME} Terminal Theme Wizard")
    print("=" * 32)
    print("Type help, back, restart, or quit at any prompt.")

    if initial_state is None:
        try:
            state, stage = choose_start_state()
        except WizardBack:
            state, stage = {}, 0
    else:
        state = initial_state.copy()
        stage = 0 if start_stage is None else start_stage
    state["output_dir"] = output_dir
    while stage <= 9:
        try:
            if stage == 0:
                palette_value = ask(
                    "Paste Coolors URL or hex colors separated by spaces",
                    "25ced1 ffffff fceade ff8a5b ea526f",
                    allow_back=False,
                )
                state["colors"] = parse_palette_input(palette_value)
                state["palette_source"] = palette_value
                log_used_url(palette_value, state["colors"])
                preview_palette(state["colors"])
                stage += 1
            elif stage == 1:
                preview_families()
                family_choice = choose_number(
                    "Choose theme family", len(THEME_FAMILIES), 1
                )
                state["family"] = THEME_FAMILIES[family_choice - 1]
                stage += 1
            elif stage == 2:
                print("\nVariant modes:")
                print("  1. balanced")
                print("  2. soft")
                print("  3. bright")
                mode_choice = choose_number("Choose variant mode", 3, 1)
                state["mode"] = ["balanced", "soft", "bright"][mode_choice - 1]
                stage += 1
            elif stage == 3:
                if state.get("background"):
                    print(
                        f"\nCurrent background: #{state['background']} {ansi_bg(state['background'])}"
                    )
                    if confirm_yes("Keep current background? y/n", default=True):
                        stage += 1
                        continue
                preview_backgrounds(state["family"])
                bg_choice = choose_number(
                    "Choose background", len(state["family"]["backgrounds"]), 1
                )
                state["background"] = state["family"]["backgrounds"][bg_choice - 1][1]
                stage += 1
            elif stage == 4:
                custom_bg = ask(
                    "Custom background hex, or press Enter to keep chosen", ""
                )
                if custom_bg:
                    state["background"] = clean_hex(custom_bg)
                stage += 1
            elif stage == 5:
                state["preview_labels"] = choose_preview_labels()
                stage += 1
            elif stage == 6:
                if state.get("foreground"):
                    print(
                        f"\nCurrent normal text: #{state['foreground']} {ansi_fg(state['foreground'], state['preview_labels']['normal'])}"
                    )
                    if not confirm_yes(
                        "Keep current normal text color? y/n", default=True
                    ):
                        state["foreground"] = choose_foreground(
                            state["colors"],
                            state["family"],
                            state["background"],
                            state["preview_labels"],
                        )
                else:
                    state["foreground"] = choose_foreground(
                        state["colors"],
                        state["family"],
                        state["background"],
                        state["preview_labels"],
                    )
                stage += 1
            elif stage == 7:
                state["roles"] = choose_role_mapping(
                    state["colors"],
                    state["family"],
                    state["mode"],
                    state.get("roles"),
                )
                state["roles"] = offer_bright_ansi_suggestions(
                    state["roles"], state["family"]
                )
                stage += 1
            elif stage == 8:
                preview_theme(
                    state["colors"],
                    state["background"],
                    state["foreground"],
                    state["roles"],
                    state["preview_labels"],
                )
                default_name = state.get(
                    "name",
                    f"Coolors {state['family']['label']} {state['mode'].title()} Theme",
                )
                state["name"] = ask("Theme name", default_name)
                stage += 1
            elif stage == 9:
                output_dir = state.get("output_dir", OUTPUT_DIR)
                if "formats" not in state:
                    state["formats"] = choose_export_formats()
                format_labels = ", ".join(state["formats"])
                print(f"\nReady to export: {state['name']}")
                print(f"Selected formats: {format_labels}")
                if not confirm_yes("Create these files? y/n", default=True):
                    print("Cancelled.")
                    return
                model = make_theme_model(
                    state["colors"],
                    state["background"],
                    state["foreground"],
                    state["mode"],
                    state["family"],
                    state["roles"],
                    state.get("palette_source", ""),
                    state["name"],
                )
                written, skipped = export_theme_files_interactive(
                    model, output_dir, state["formats"]
                )
                print_export_results(written, skipped)
                offer_parallel_themes(
                    state["colors"],
                    state["family"],
                    state["mode"],
                    state["name"],
                    output_dir,
                    state["formats"],
                )
                if "iterm" in state["formats"]:
                    print("\nImport in iTerm:")
                    print("Settings → Profiles → Colors → Color Presets → Import")
                print("\nDone.")
                return
        except WizardBack:
            stage = max(0, stage - 1)
            print("Back.")
        except ValueError as error:
            print(error)


def build_parser():
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME}: make terminal color themes from Coolors URLs or hex palettes."
    )
    parser.add_argument(
        "--palette", help="Coolors URL or hex colors separated by spaces."
    )
    parser.add_argument(
        "--edit",
        type=Path,
        help="Start by editing an existing iTerm .itermcolors file.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=OUTPUT_DIR,
        help="Output directory for exported themes.",
    )
    parser.add_argument(
        "--format",
        dest="formats",
        help="Export formats: all, data, or any of iterm, kitty, alacritty, wezterm, data.",
    )
    parser.add_argument(
        "--list-themes",
        action="store_true",
        help="List existing iTerm themes in the output directory.",
    )
    parser.add_argument(
        "--about",
        action="store_true",
        help="Show credits and project information.",
    )
    parser.add_argument(
        "--no-splash",
        action="store_true",
        help="Skip the interactive startup banner.",
    )
    parser.add_argument(
        "--version", action="version", version=f"{APP_NAME} {APP_VERSION}"
    )
    return parser


def initial_state_from_args(args):
    state = {}
    stage = 0
    if args.edit:
        state = load_theme_state(args.edit)
        stage = 1
    elif args.palette:
        state["colors"] = parse_palette_input(args.palette)
        state["palette_source"] = args.palette
        preview_palette(state["colors"])
        stage = 1

    if args.formats:
        state["formats"] = parse_export_formats(args.formats)
    return state or None, stage


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.about:
        print(about_text())
        return
    if args.list_themes:
        themes = (
            sorted(path for path in args.out.glob("*.itermcolors") if path.is_file())
            if args.out.exists()
            else []
        )
        if not themes:
            print(f"No themes found in {args.out}")
            return
        for path in themes:
            print(path)
        return

    initial_state, start_stage = initial_state_from_args(args)
    pure_wizard = not any((args.palette, args.edit, args.formats))
    if pure_wizard and not args.no_splash:
        show_splash(wait=True)
    while True:
        try:
            run_wizard(initial_state, start_stage, args.out)
            return
        except WizardRestart:
            print("\nRestarting.")
            initial_state, start_stage = None, 0
        except WizardQuit:
            print("Cancelled.")
            return


if __name__ == "__main__":
    main()
