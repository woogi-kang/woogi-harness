from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from tailwind_config_gen import TailwindConfigGenerator, parse_fonts, parse_pairs


def test_default_is_tailwind4_css(tmp_path):
    generator = TailwindConfigGenerator(output_path=tmp_path / "theme.css")
    assert generator.output_path.name == "theme.css"
    assert '@import "tailwindcss";' in generator.generate_config_string()
    assert "tailwind.config" not in generator.generate_config_string()


def test_generates_css_first_tokens_and_plugins(tmp_path):
    generator = TailwindConfigGenerator(
        framework="nextjs", output_path=tmp_path / "theme.css"
    )
    generator.add_colors({"brand": "oklch(0.6 0.18 250)"})
    generator.add_fonts({"product": ["Project Sans", "system-ui", "sans-serif"]})
    generator.add_spacing({"workspace": "1.125rem"})
    generator.add_breakpoints({"wide": "90rem"})
    generator.add_plugins(["@tailwindcss/typography", "@tailwindcss/typography"])
    content = generator.generate_config_string()
    assert "--color-brand: oklch(0.6 0.18 250);" in content
    assert '--font-product: "Project Sans", system-ui, sans-serif;' in content
    assert "--spacing-workspace: 1.125rem;" in content
    assert "--breakpoint-wide: 90rem;" in content
    assert content.count('@plugin "@tailwindcss/typography";') == 1


def test_palette_does_not_fabricate_unverified_shades():
    generator = TailwindConfigGenerator()
    generator.add_color_palette("brand", "#336699")
    assert generator.tokens == {"--color-brand-500": "#336699"}


def test_write_and_validate(tmp_path):
    output = tmp_path / "nested" / "theme.css"
    generator = TailwindConfigGenerator(output_path=output)
    generator.add_colors({"primary": "#336699"})
    success, message = generator.write_config()
    assert success is True
    assert "Tailwind 4" in message
    assert output.exists()


def test_rejects_invalid_token_and_plugin():
    generator = TailwindConfigGenerator()
    try:
        generator.add_colors({"Bad Name": "#fff"})
    except ValueError as exc:
        assert "invalid Tailwind token name" in str(exc)
    else:
        raise AssertionError("invalid token was accepted")
    try:
        generator.add_plugins(['bad"plugin'])
    except ValueError as exc:
        assert "invalid plugin" in str(exc)
    else:
        raise AssertionError("invalid plugin was accepted")


def test_no_automatic_plugin_recommendations():
    assert TailwindConfigGenerator(framework="nextjs").recommend_plugins() == []


def test_pair_and_font_parsers():
    assert parse_pairs(["brand:#123456"], "color") == {"brand": "#123456"}
    assert parse_fonts(["product:Project Sans,system-ui"]) == {
        "product": ["Project Sans", "system-ui"]
    }
