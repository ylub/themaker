# THEMaker

THEMaker turns a Coolors palette or a list of hex colors into terminal color
themes.

It currently exports:

- iTerm2 `.itermcolors`
- Kitty `.conf`
- Alacritty `.toml`
- WezTerm `.lua`
- Source `.yaml` for terminal color scheme repos
- Portable JSON theme data for someone else or another tool to export later

THEMaker uses only the Python standard library.

## Quick Start

Run the wizard:

```bash
python3 themaker.py
```

Check the version:

```bash
python3 themaker.py --version
```

Use a palette from the command line and continue in the wizard:

```bash
python3 themaker.py --palette "25ced1 ffffff fceade ff8a5b ea526f"
```

Hex colors may be written as 6-digit RGB, 8-digit RGBA, or short 4-digit RGBA.
Alpha values are accepted for convenience and ignored when exporting terminal
themes.

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

Show credits and project information:

```bash
python3 themaker.py --about
```

Skip the startup banner in interactive mode:

```bash
python3 themaker.py --no-splash
```

## Export Choices

At the save step, THEMaker asks what to export:

- `all` exports every supported format
- `one` asks for a single format
- `some` asks for multiple formats
- `data` saves only portable JSON theme data

Supported format names are:

```text
iterm kitty alacritty wezterm yaml data
```

| Format | Extension | Use |
| --- | --- | --- |
| `iterm` | `.itermcolors` | Import into iTerm2. |
| `kitty` | `.conf` | Include or copy into Kitty config. |
| `alacritty` | `.toml` | Import or copy into Alacritty config. |
| `wezterm` | `.lua` | Require or copy into WezTerm config. |
| `yaml` | `.yaml` | Submit source schemes to terminal color scheme repos. |
| `data` | `.json` | Save portable theme data for another tool or maintainer. |

If a target file already exists, the wizard asks before overwriting it.

## Examples

The `examples/` folder contains one sample palette exported to every supported
format. These files are useful for checking the output shape before importing a
theme into your own terminal.

## Using Exported Themes

iTerm2:

On macOS, opening the generated `.itermcolors` file will import it into iTerm2.
You can also import it manually:

1. Open Settings.
2. Go to Profiles, then Colors.
3. Open Color Presets.
4. Choose Import and select the `.itermcolors` file.

Kitty:

```bash
include /path/to/theme.conf
```

Add that line to your Kitty config, or copy the generated color lines into it.

Alacritty:

```toml
import = ["/path/to/theme.toml"]
```

Add that to your Alacritty config, or copy the generated `[colors]` sections
into it.

WezTerm:

```lua
local theme = require("theme")

return {
  colors = theme,
}
```

Put the generated `.lua` file somewhere WezTerm can require it, or copy the
returned table into your WezTerm config.

YAML:

The `.yaml` export follows the source scheme guidance from
[`yaml/README.md` in `mbadolato/iTerm2-Color-Schemes`](https://github.com/mbadolato/iTerm2-Color-Schemes/blob/master/yaml/README.md).
It writes `color_01` through `color_16`, plus the optional extra keys described
there, including `badge`, `bold`, `cursor_guide`, `cursor_text`, `link`,
`selection_text`, `selection`, `tab`, and `underline`.

## Contributing Schemes

For terminal color scheme repositories that accept source YAML files, export
with:

```bash
python3 themaker.py --format yaml
```

Review the generated file before submitting it, especially the theme name,
normal ANSI colors, bright ANSI colors, selection colors, and cursor colors.

## Bright And Sibling Suggestions

After ANSI colors are chosen, THEMaker can suggest brighter ANSI colors for the
same theme. These are previewed as `current -> suggested` and are only applied
if you confirm.

When you customize ANSI roles, THEMaker also offers extra color suggestions.
Those include palette complements and a few palette-fit accent colors tuned to
the selected theme family.

After exporting a theme, THEMaker can also suggest sibling themes from the same
palette, such as a bright pastel variant or a softer dark variant. These are
also opt-in.

## Tests

Run:

```bash
python3 -m unittest
```

## Releases

The first public release should be tagged as `v0.2.0` after the public export
branch is merged.

## Credits

Created by [@ylub](https://github.com/ylub).

Project repo: [github.com/ylub/themaker](https://github.com/ylub/themaker).

Built with help from Codex.

Inspired by palette ideas from [Coolors](https://coolors.co).
