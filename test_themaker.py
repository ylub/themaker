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
            themaker.parse_palette_input("https://coolors.co/25ced1-ffffff-fceade-ff8a5b-ea526f"),
            expected,
        )

    def test_parse_palette_input_rejects_short_palette(self):
        with self.assertRaises(ValueError):
            themaker.parse_palette_input("25ced1 ffffff")

    def test_theme_model_has_terminal_colors(self):
        model = self.build_model()
        self.assertEqual(model["palette"], "#25CED1 #FFFFFF #FCEADE #FF8A5B #EA526F")
        self.assertEqual(len(model["colors"]["ansi"]), 8)
        self.assertEqual(len(model["colors"]["bright"]), 8)

    def test_exporters_write_expected_files(self):
        model = self.build_model()
        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory)
            written, skipped = themaker.export_theme_files(
                model,
                out_dir,
                ["iterm", "kitty", "alacritty", "wezterm", "data"],
            )
            self.assertEqual(skipped, [])
            self.assertEqual(len(written), 5)
            self.assertTrue((out_dir / "sample.itermcolors").exists())
            self.assertIn("foreground #F8F8F2", (out_dir / "sample.conf").read_text())
            self.assertIn("[colors.primary]", (out_dir / "sample.toml").read_text())
            self.assertIn("return {", (out_dir / "sample.lua").read_text())
            self.assertIn('"palette"', (out_dir / "sample.json").read_text())

            with (out_dir / "sample.itermcolors").open("rb") as handle:
                plist = plistlib.load(handle)
            self.assertEqual(plist[themaker.ORIGINAL_PALETTE_KEY], model["palette"])

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
        self.assertEqual(set(suggestions), {"red", "green", "yellow", "blue", "magenta", "cyan"})
        for color in suggestions.values():
            self.assertEqual(themaker.clean_hex(color), color)


if __name__ == "__main__":
    unittest.main()
