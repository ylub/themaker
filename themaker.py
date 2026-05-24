#!/usr/bin/env python3
import plistlib
import re
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path

DEFAULT_FG = "F8F8F2"
APP_DIR = Path(__file__).resolve().parent
URL_LOG_FILE = APP_DIR / "used_urls.log"
OUTPUT_DIR = APP_DIR / "colors"
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


def clean_hex(h):
    h = h.strip().lstrip("#")
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        raise ValueError(f"Invalid hex color: {h}")
    return h.upper()


def hex_to_rgb(hex_color):
    h = clean_hex(hex_color)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_plist(hex_color):
    r, g, b = hex_to_rgb(hex_color)
    return {
        "Red Component": r / 255,
        "Green Component": g / 255,
        "Blue Component": b / 255,
        "Alpha Component": 1.0,
        "Color Space": "sRGB",
    }


def parse_palette_input(value):
    raw_value = value.strip()
    parsed_url = urlparse(raw_value)
    palette_text = parsed_url.path.rstrip("/").split("/")[-1] if parsed_url.scheme or parsed_url.netloc else raw_value
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


def ansi_bg(hex_color, text="      "):
    return ansi_swatch(hex_color, text)


def ansi_fg(hex_color, text):
    r, g, b = hex_to_rgb(hex_color)
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"


def preview_palette(colors):
    print("\nPalette:")
    for i, c in enumerate(colors, 1):
        print(f"  {i}. #{c} {ansi_bg(c)}")


def preview_palette_choices(colors):
    print("\nPalette choices:")
    for i, color in enumerate(colors, 1):
        print(f"  {i}. #{color} {ansi_bg(color)}")


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
        print(f"  {i}. #{color} {ansi_bg(color)}  {name}")


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
        error_note = " close to error" if color_distance(color, error_color) < 90 else ""
        bg_note = " low background contrast" if color_distance(color, background) < 90 else ""
        print(f"  {index}. #{color} {ansi_fg(color, labels['normal'])}  {name}{error_note}{bg_note}")


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
        ("Background", background),
        ("Foreground", foreground),
        ("Black / ANSI 0 / base", roles["black"]),
        ("Red / ANSI 1 / error", roles["red"]),
        ("Green / ANSI 2 / success", roles["green"]),
        ("Yellow / ANSI 3 / warning", roles["yellow"]),
        ("Blue / ANSI 4 / link", roles["blue"]),
        ("Magenta / ANSI 5 / highlight", roles["magenta"]),
        ("Cyan / ANSI 6 / accent", roles["cyan"]),
        ("White / ANSI 7", foreground),
    ]

    print("\nTheme preview:")
    for label, color in mapping:
        print(f"  {label:<28} #{color} {ansi_bg(color)}")

    print("\nText preview:")
    print(f"  {ansi_bg(background, '  ')} "
          f"{ansi_fg(foreground, labels['normal'])} (foreground) "
          f"{ansi_fg(roles['cyan'], labels['accent'])} (ANSI 6/cyan/accent) "
          f"{ansi_fg(roles['yellow'], labels['warning'])} (ANSI 3/yellow/warning) "
          f"{ansi_fg(roles['red'], labels['error'])} (ANSI 1/red/error)")
    if color_distance(foreground, roles["red"]) < 90:
        print("  Warning: normal text is close to the error color.")
    if color_distance(foreground, background) < 90:
        print("  Warning: normal text is close to the background color.")


def make_theme(colors, background, foreground, mode, family, roles):
    sorted_colors = sorted(colors, key=brightness)

    if mode == "soft":
        ansi8 = sorted_colors[1]
    elif mode == "bright":
        ansi8 = sorted_colors[2]
    else:
        ansi8 = roles["bright_black"]

    return {
        "Background Color": rgb_plist(background),
        "Foreground Color": rgb_plist(foreground),
        "Bold Color": rgb_plist(foreground),
        "Cursor Color": rgb_plist(roles["cyan"]),
        "Cursor Text Color": rgb_plist(background),
        "Selection Color": rgb_plist(family["selection"]),
        "Selected Text Color": rgb_plist(background),

        "Ansi 0 Color": rgb_plist(roles["black"]),
        "Ansi 1 Color": rgb_plist(roles["red"]),
        "Ansi 2 Color": rgb_plist(roles["green"]),
        "Ansi 3 Color": rgb_plist(roles["yellow"]),
        "Ansi 4 Color": rgb_plist(roles["blue"]),
        "Ansi 5 Color": rgb_plist(roles["magenta"]),
        "Ansi 6 Color": rgb_plist(roles["cyan"]),
        "Ansi 7 Color": rgb_plist(foreground),

        "Ansi 8 Color": rgb_plist(ansi8),
        "Ansi 9 Color": rgb_plist(roles["red"]),
        "Ansi 10 Color": rgb_plist(roles["green"]),
        "Ansi 11 Color": rgb_plist(roles["yellow"]),
        "Ansi 12 Color": rgb_plist(roles["blue"]),
        "Ansi 13 Color": rgb_plist(roles["magenta"]),
        "Ansi 14 Color": rgb_plist(roles["cyan"]),
        "Ansi 15 Color": rgb_plist(foreground),
    }


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
        val = input(f"{prompt}{suffix}: ").strip()
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
        print(
            f"  ANSI {role:<7} / {preview_name:<17} "
            f"#{roles[role]} {ansi_bg(roles[role])} {color_choice_label(colors, roles[role])}"
        )


def choose_role_color(colors, role, current_color):
    prompt = f"ANSI {role} color: palette 1-{len(colors)}, custom hex, or Enter to keep"
    raw = ask(prompt, "").strip()
    if not raw:
        return current_color
    if raw.isdigit() and 1 <= int(raw) <= len(colors):
        return colors[int(raw) - 1]
    try:
        return clean_hex(raw)
    except ValueError as error:
        print(error)
        return choose_role_color(colors, role, current_color)


def choose_role_mapping(colors, family):
    roles = palette_roles(colors, family)
    print_role_mapping(colors, roles)
    customize = ask("Change which palette colors feed the ANSI roles? y/n", "n").strip().lower()
    if customize not in {"y", "yes"}:
        return roles

    print("\nUse palette numbers from above, or type a custom hex.")
    preview_palette_choices(colors)
    for role in ("red", "green", "yellow", "blue", "magenta", "cyan"):
        roles[role] = choose_role_color(colors, role, roles[role])
    print_role_mapping(colors, roles)
    return roles


def preview_label_defaults() -> str:
    return " | ".join(DEFAULT_PREVIEW_LABELS[key] for key in ("normal", "accent", "warning", "error"))


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


def run_wizard():
    print("\nCoolors → iTerm Theme Wizard")
    print("=" * 32)
    print("Type help, back, restart, or quit at any prompt.")

    state = {}
    stage = 0
    while stage <= 9:
        try:
            if stage == 0:
                palette_value = ask(
                    "Paste Coolors URL or hex colors separated by spaces",
                    "25ced1 ffffff fceade ff8a5b ea526f",
                    allow_back=False,
                )
                state["colors"] = parse_palette_input(palette_value)
                log_used_url(palette_value, state["colors"])
                preview_palette(state["colors"])
                stage += 1
            elif stage == 1:
                preview_families()
                family_choice = choose_number("Choose theme family", len(THEME_FAMILIES), 1)
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
                preview_backgrounds(state["family"])
                bg_choice = choose_number("Choose background", len(state["family"]["backgrounds"]), 1)
                state["background"] = state["family"]["backgrounds"][bg_choice - 1][1]
                stage += 1
            elif stage == 4:
                custom_bg = ask("Custom background hex, or press Enter to keep chosen", "")
                if custom_bg:
                    state["background"] = clean_hex(custom_bg)
                stage += 1
            elif stage == 5:
                state["preview_labels"] = choose_preview_labels()
                stage += 1
            elif stage == 6:
                state["foreground"] = choose_foreground(
                    state["colors"],
                    state["family"],
                    state["background"],
                    state["preview_labels"],
                )
                stage += 1
            elif stage == 7:
                state["roles"] = choose_role_mapping(state["colors"], state["family"])
                stage += 1
            elif stage == 8:
                preview_theme(
                    state["colors"],
                    state["background"],
                    state["foreground"],
                    state["roles"],
                    state["preview_labels"],
                )
                default_name = f"Coolors {state['family']['label']} {state['mode'].title()} Theme"
                state["name"] = ask("Theme name", default_name)
                stage += 1
            elif stage == 9:
                OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
                out_path = OUTPUT_DIR / f"{safe_filename(state['name'])}.itermcolors"
                if not confirm_yes("Create this iTerm theme? y/n", default=True):
                    print("Cancelled.")
                    return
                theme = make_theme(
                    state["colors"],
                    state["background"],
                    state["foreground"],
                    state["mode"],
                    state["family"],
                    state["roles"],
                )
                with out_path.open("wb") as f:
                    plistlib.dump(theme, f)
                print("\nCreated:")
                print(out_path)
                print("\nImport in iTerm:")
                print("Settings → Profiles → Colors → Color Presets → Import")
                return
        except WizardBack:
            stage = max(0, stage - 1)
            print("Back.")
        except ValueError as error:
            print(error)


def main():
    while True:
        try:
            run_wizard()
            return
        except WizardRestart:
            print("\nRestarting.")
        except WizardQuit:
            print("Cancelled.")
            return


if __name__ == "__main__":
    main()
