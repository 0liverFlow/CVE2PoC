import io

from rich.console import Console

from CVE2PoC.core import theme


def test_variant_parse():
    assert theme._parse_variant("rose-pine") == "main"
    assert theme._parse_variant("Rose-Pine-Moon") == "moon"
    assert theme._parse_variant("dawn") == "dawn"
    assert theme._parse_variant("light") == "dawn"
    assert theme._parse_variant("nonsense") is None


def test_palettes_share_keys_and_are_hex():
    keys = set(theme.MAIN)
    assert keys == set(theme.MOON) == set(theme.DAWN)
    for palette in (theme.MAIN, theme.MOON, theme.DAWN):
        for value in palette.values():
            assert value.startswith("#") and len(value) == 7


def test_legacy_colour_names_remap_to_palette():
    con = Console(
        theme=theme.build_theme(theme.MAIN),
        force_terminal=True,
        color_system="truecolor",
        file=io.StringIO(),
    )
    con.print("[red3]x[/red3] [gold1]y[/gold1] [spring_green2]z[/spring_green2]")
    out = con.file.getvalue()
    assert "235;111;146" in out  # love  <- red3
    assert "246;193;119" in out  # gold  <- gold1
    assert "156;207;216" in out  # foam  <- spring_green2


def test_ansi_fg_modes():
    assert theme.ansi_fg("#c4a7e7", "truecolor") == "\x1b[38;2;196;167;231m"
    assert theme.ansi_fg("#c4a7e7", "256").startswith("\x1b[38;5;")
    assert theme.ansi_fg("#c4a7e7", "none") == ""


def test_to_256_bounds():
    assert theme._to_256(0, 0, 0) == 16
    assert theme._to_256(255, 255, 255) == 231
    assert theme._to_256(128, 128, 128) >= 232  # grey ramp
