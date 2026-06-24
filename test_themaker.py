import contextlib
import io
import json
import plistlib
import tempfile
import unittest
from pathlib import Path

import themaker

PALETTE = "25ced1 ffffff fceade ff8a5b ea526f"


class TheMakerTests(unittest.TestCase):
    def build_model(self):
        colors = themaker.parse_palette_input(PALETTE)
        family = themaker.THEME_FAMILIES[0]
        roles = themaker.palette_roles(colors, family)
        return themaker.make_theme_model(
            colors,
            "101418",
            "F8F8F2",
            "balanced",
            family,
            roles,
            PALETTE,
            "sample",
        )

    def test_parse_palette_input_accepts_hex_and_coolors_url(self):
        expected = ["25CED1", "FFFFFF", "FCEADE", "FF8A5B", "EA526F"]
        self.assertEqual(themaker.parse_palette_input(PALETTE), expected)
        self.assertEqual(
            themaker.parse_palette_input(
                "https://coolors.co/25ced1-ffffff-fceade-ff8a5b-ea526f"
            ),
            expected,
        )

    def test_parse_palette_input_accepts_alpha_hex(self):
        self.assertEqual(
            themaker.parse_palette_input("#abcd 11223344 25ced1ff ffffff80 00000000"),
            ["AABBCC", "112233", "25CED1", "FFFFFF", "000000"],
        )

    def test_parse_palette_input_rejects_short_palette(self):
        with self.assertRaises(ValueError):
            themaker.parse_palette_input("25ced1 ffffff")

    def test_role_preview_label_defaults_to_terminal_wording(self):
        self.assertEqual(themaker.role_preview_label("red"), "error")
        self.assertEqual(themaker.role_preview_label("cyan"), "accent")

    def test_role_preview_label_supports_tuxedo_wording(self):
        self.assertEqual(
            themaker.role_preview_label("red", "tuxedo"),
            "priority A, overdue dates, today",
        )
        self.assertEqual(
            themaker.role_preview_label("cyan", "tuxedo"),
            "search matches",
        )
        self.assertEqual(themaker.tuxedo_role_keys("magenta"), "pri_other, context")
        self.assertEqual(themaker.tuxedo_role_keys("cyan"), "matched")

    def test_role_preview_label_supports_coteditor_wording(self):
        self.assertEqual(
            themaker.role_preview_label("cyan", "coteditor"),
            "commands and attributes",
        )
        self.assertEqual(
            themaker.role_preview_label("yellow", "coteditor"),
            "types, characters, and highlight",
        )
        self.assertEqual(
            themaker.coteditor_role_keys("magenta"),
            "values, numbers",
        )

    def test_preview_label_defaults_are_target_specific(self):
        self.assertEqual(
            themaker.preview_label_defaults("terminal"),
            "normal text | accent | warning | error",
        )
        self.assertEqual(
            themaker.preview_label_defaults("tuxedo"),
            "task title | matched text | due date | priority A",
        )
        self.assertEqual(
            themaker.preview_label_defaults("coteditor"),
            "variable | command | type | keyword",
        )

    def test_parse_preview_labels_uses_tuxedo_defaults(self):
        self.assertEqual(
            themaker.parse_preview_labels("", "tuxedo"),
            {
                "normal": "task title",
                "accent": "matched text",
                "warning": "due date",
                "error": "priority A",
            },
        )

    def test_tuxedo_foreground_warning_says_priority_a(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            themaker.preview_foregrounds(
                [("Soft white", "F8F8F2")],
                "101418",
                "F3F3F4",
                themaker.preview_labels_for_target("tuxedo"),
                "tuxedo",
            )
        self.assertIn("close to priority A", output.getvalue())
        self.assertNotIn("close to error", output.getvalue())

    def test_coteditor_foreground_warning_says_syntax_accent(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            themaker.preview_foregrounds(
                [("Soft white", "F8F8F2")],
                "101418",
                "F3F3F4",
                themaker.preview_labels_for_target("coteditor"),
                "coteditor",
            )
        self.assertIn("close to syntax accent", output.getvalue())
        self.assertNotIn("close to error", output.getvalue())

    def test_theme_model_has_terminal_colors(self):
        model = self.build_model()
        self.assertEqual(model["palette"], "#25CED1 #FFFFFF #FCEADE #FF8A5B #EA526F")
        self.assertEqual(len(model["colors"]["ansi"]), 8)
        self.assertEqual(len(model["colors"]["bright"]), 8)

    def test_bright_terminal_slots_differ_from_normal_colors(self):
        colors = themaker.parse_palette_input("f25757 8085b3 84a07c c3d350 eff68d")
        family = themaker.THEME_FAMILIES[0]
        roles = {
            "black": "101418",
            "red": "FF5252",
            "green": "87F069",
            "yellow": "F3FF52",
            "blue": "616FEF",
            "magenta": "D269F0",
            "cyan": "52FFFF",
            "bright_black": "E0F06A",
        }
        model = themaker.make_theme_model(
            colors,
            "101418",
            "EAF6FF",
            "balanced",
            family,
            roles,
            "",
            "one second test",
        )
        for normal, bright in zip(
            model["colors"]["ansi"][1:7], model["colors"]["bright"][1:7]
        ):
            self.assertNotEqual(normal, bright)
        self.assertEqual(model["colors"]["bright"][7], "FFFFFF")

    def test_exporters_write_expected_files(self):
        model = self.build_model()
        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory)
            written, skipped = themaker.export_theme_files(
                model,
                out_dir,
                [
                    "iterm",
                    "terminal",
                    "kitty",
                    "alacritty",
                    "wezterm",
                    "coteditor",
                    "tuxedo",
                    "yaml",
                    "data",
                ],
            )
            self.assertEqual(skipped, [])
            self.assertEqual(len(written), 9)
            self.assertTrue((out_dir / "sample.itermcolors").exists())
            self.assertTrue((out_dir / "sample.terminal").exists())
            self.assertIn("foreground #F8F8F2", (out_dir / "sample.conf").read_text())
            self.assertIn("[colors.primary]", (out_dir / "sample.toml").read_text())
            self.assertIn("return {", (out_dir / "sample.lua").read_text())
            cottheme = json.loads((out_dir / "sample.cottheme").read_text())
            self.assertEqual(cottheme["background"]["color"], "#101418")
            self.assertEqual(cottheme["text"]["color"], "#F8F8F2")
            self.assertEqual(cottheme["metadata"]["author"], "@ylub")
            tuxedo_text = (out_dir / "sample.tuxedo.toml").read_text()
            self.assertIn("name = sample", tuxedo_text)
            self.assertIn("bg = #101418", tuxedo_text)
            self.assertIn("pri_a = #EA526F", tuxedo_text)
            yaml_text = (out_dir / "sample.yaml").read_text()
            self.assertIn('color_01: "#101418"', yaml_text)
            self.assertIn('color_16: "#FFFFFF"', yaml_text)
            self.assertIn('badge: "#FFFFFF"', yaml_text)
            self.assertIn('selection_text: "#101418"', yaml_text)
            self.assertIn('"palette"', (out_dir / "sample.json").read_text())

            with (out_dir / "sample.itermcolors").open("rb") as handle:
                plist = plistlib.load(handle)
            self.assertEqual(plist[themaker.ORIGINAL_PALETTE_KEY], model["palette"])
            with (out_dir / "sample.terminal").open("rb") as handle:
                terminal_plist = plistlib.load(handle)
            self.assertEqual(terminal_plist["TextColor"], themaker.rgb_plist("F8F8F2"))
            self.assertEqual(
                terminal_plist["ANSIBrightRedColor"],
                themaker.rgb_plist(model["colors"]["bright"][1]),
            )

    def test_existing_files_skip_without_overwrite(self):
        model = self.build_model()
        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory)
            themaker.export_theme_files(model, out_dir, ["kitty"])
            written, skipped = themaker.export_theme_files(model, out_dir, ["kitty"])
            self.assertEqual(written, [])
            self.assertEqual(skipped, [out_dir / "sample.conf"])

    def test_bright_role_suggestions_are_valid_hex(self):
        colors = themaker.parse_palette_input(PALETTE)
        family = themaker.THEME_FAMILIES[0]
        roles = themaker.palette_roles(colors, family)
        suggestions = themaker.bright_role_suggestions(roles, family)
        self.assertEqual(
            set(suggestions), {"red", "green", "yellow", "blue", "magenta", "cyan"}
        )
        for color in suggestions.values():
            self.assertEqual(themaker.clean_hex(color), color)
        self.assertTrue(any(suggestions[role] != roles[role] for role in suggestions))

    def test_extra_color_options_include_complements_and_palette_fit_colors(self):
        colors = themaker.parse_palette_input("ef4444 22c55e ec4899 a3a3a3 f8fafc")
        family = themaker.THEME_FAMILIES[0]
        options = themaker.extra_color_options(colors, family, "balanced")
        names = [name for name, _color in options]
        self.assertTrue(any("Complement" in name for name in names))
        self.assertTrue(any("Palette-fit" in name for name in names))
        self.assertLessEqual(
            sum(1 for name in names if name.startswith("Palette-fit")), 4
        )
        for _name, color in options:
            self.assertEqual(themaker.clean_hex(color), color)

    def test_tuxedo_extra_color_options_add_missing_priority_colors(self):
        colors = themaker.parse_palette_input("3b82f6 6366f1 8b5cf6 64748b e2e8f0")
        family = themaker.THEME_FAMILIES[0]
        options = themaker.extra_color_options(colors, family, "balanced", "tuxedo")
        names = [name for name, _color in options]
        self.assertIn("Tuxedo priority A reddish fallback", names)
        self.assertIn("Tuxedo priority B yellowish fallback", names)
        self.assertIn("Tuxedo priority C greenish fallback", names)
        for _name, color in options:
            self.assertEqual(themaker.clean_hex(color), color)

    def test_tuxedo_extra_color_options_skip_priority_colors_already_present(self):
        colors = themaker.parse_palette_input("ef4444 eab308 22c55e 64748b e2e8f0")
        family = themaker.THEME_FAMILIES[0]
        options = themaker.extra_color_options(colors, family, "balanced", "tuxedo")
        names = [name for name, _color in options]
        self.assertNotIn("Tuxedo priority A reddish fallback", names)
        self.assertNotIn("Tuxedo priority B yellowish fallback", names)
        self.assertNotIn("Tuxedo priority C greenish fallback", names)

    def test_tuxedo_edits_only_semantic_roles(self):
        self.assertEqual(
            themaker.editable_role_names("tuxedo"),
            ("red", "yellow", "green", "magenta", "cyan"),
        )

    def test_terminal_edits_all_ansi_roles(self):
        self.assertEqual(
            themaker.editable_role_names("terminal"),
            ("red", "green", "yellow", "blue", "magenta", "cyan"),
        )

    def test_coteditor_edits_only_syntax_roles(self):
        self.assertEqual(
            themaker.editable_role_names("coteditor"),
            ("cyan", "yellow", "blue", "magenta", "green"),
        )

    def test_tuxedo_bright_suggestions_only_apply_semantic_roles(self):
        roles = {
            "black": "101418",
            "red": "EF4444",
            "green": "22C55E",
            "yellow": "EAB308",
            "blue": "3B82F6",
            "magenta": "F97316",
            "cyan": "38BDF8",
            "bright_black": "64748B",
        }
        family = themaker.THEME_FAMILIES[0]
        suggestions = themaker.bright_role_suggestions(roles, family)
        updated = roles.copy()
        for role in themaker.editable_role_names("tuxedo"):
            updated[role] = suggestions[role]
        updated["blue"] = updated["green"]
        self.assertEqual(updated["blue"], updated["green"])

    def test_interactive_export_formats_are_target_specific(self):
        self.assertEqual(
            themaker.export_formats_for_target("terminal"),
            (
                "iterm",
                "terminal",
                "kitty",
                "alacritty",
                "wezterm",
                "yaml",
                "data",
            ),
        )
        self.assertEqual(
            themaker.export_formats_for_target("tuxedo"),
            ("tuxedo", "data"),
        )
        self.assertEqual(
            themaker.export_formats_for_target("coteditor"),
            ("coteditor", "data"),
        )


if __name__ == "__main__":
    unittest.main()
