# THEMaker

THEMaker turns a Coolors palette or a list of hex colors into terminal color
themes.

It currently exports:

- iTerm2 `.itermcolors`
- Kitty `.conf`
- Alacritty `.toml`
- WezTerm `.lua`
- Portable JSON theme data for someone else or another tool to export later

THEMaker uses only the Python standard library.

## Quick Start

Run the wizard:

```bash
python3 themaker.py
```

Use a palette from the command line and continue in the wizard:

```bash
python3 themaker.py --palette "25ced1 ffffff fceade ff8a5b ea526f"
```

Choose export formats up front:

```bash
python3 themaker.py --palette "25ced1 ffffff fceade ff8a5b ea526f" --format "iterm kitty"
```

Save somewhere else:

```bash
python3 themaker.py --out ./exports
```

Edit an existing iTerm theme:

```bash
python3 themaker.py --edit colors/example.itermcolors
```

List existing editable iTerm themes in an output folder:

```bash
python3 themaker.py --list-themes --out colors
```

## Export Choices

At the save step, THEMaker asks what to export:

- `all` exports every supported format
- `one` asks for a single format
- `some` asks for multiple formats
- `data` saves only portable JSON theme data

Supported format names are:

```text
iterm kitty alacritty wezterm data
```

If a target file already exists, the wizard asks before overwriting it.

## Bright And Sibling Suggestions

After ANSI colors are chosen, THEMaker can suggest brighter ANSI colors for the
same theme. These are previewed as `current -> suggested` and are only applied
if you confirm.

After exporting a theme, THEMaker can also suggest sibling themes from the same
palette, such as a bright pastel variant or a softer dark variant. These are
also opt-in.

## Tests

Run:

```bash
python3 -m unittest
```
