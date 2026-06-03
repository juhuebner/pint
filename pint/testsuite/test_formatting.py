from __future__ import annotations

from pint.registry import UnitRegistry
import pytest

import pint.formatting as fmt


@pytest.mark.filterwarnings("ignore::DeprecationWarning:pint*")
@pytest.mark.parametrize(
    ["format", "default", "flag", "expected"],
    (
        pytest.param(".02fD", ".3fP", True, (".02f", "D"), id="both-both-separate"),
        pytest.param(".02fD", ".3fP", False, (".02f", "D"), id="both-both-combine"),
        pytest.param(".02fD", ".3fP", None, (".02f", "D"), id="both-both-default"),
        pytest.param("D", ".3fP", True, (".3f", "D"), id="unit-both-separate"),
        pytest.param("D", ".3fP", False, ("", "D"), id="unit-both-combine"),
        pytest.param("D", ".3fP", None, ("", "D"), id="unit-both-default"),
        pytest.param(".02f", ".3fP", True, (".02f", "P"), id="magnitude-both-separate"),
        pytest.param(".02f", ".3fP", False, (".02f", ""), id="magnitude-both-combine"),
        pytest.param(".02f", ".3fP", None, (".02f", ""), id="magnitude-both-default"),
        pytest.param("D", "P", True, ("", "D"), id="unit-unit-separate"),
        pytest.param("D", "P", False, ("", "D"), id="unit-unit-combine"),
        pytest.param("D", "P", None, ("", "D"), id="unit-unit-default"),
        pytest.param(
            ".02f", ".3f", True, (".02f", ""), id="magnitude-magnitude-separate"
        ),
        pytest.param(
            ".02f", ".3f", False, (".02f", ""), id="magnitude-magnitude-combine"
        ),
        pytest.param(
            ".02f", ".3f", None, (".02f", ""), id="magnitude-magnitude-default"
        ),
        pytest.param("D", ".3f", True, (".3f", "D"), id="unit-magnitude-separate"),
        pytest.param("D", ".3f", False, ("", "D"), id="unit-magnitude-combine"),
        pytest.param("D", ".3f", None, ("", "D"), id="unit-magnitude-default"),
        pytest.param(".02f", "P", True, (".02f", "P"), id="magnitude-unit-separate"),
        pytest.param(".02f", "P", False, (".02f", ""), id="magnitude-unit-combine"),
        pytest.param(".02f", "P", None, (".02f", ""), id="magnitude-unit-default"),
        pytest.param("", ".3fP", True, (".3f", "P"), id="none-both-separate"),
        pytest.param("", ".3fP", False, (".3f", "P"), id="none-both-combine"),
        pytest.param("", ".3fP", None, (".3f", "P"), id="none-both-default"),
        pytest.param("", "P", True, ("", "P"), id="none-unit-separate"),
        pytest.param("", "P", False, ("", "P"), id="none-unit-combine"),
        pytest.param("", "P", None, ("", "P"), id="none-unit-default"),
        pytest.param("", ".3f", True, (".3f", ""), id="none-magnitude-separate"),
        pytest.param("", ".3f", False, (".3f", ""), id="none-magnitude-combine"),
        pytest.param("", ".3f", None, (".3f", ""), id="none-magnitude-default"),
        pytest.param("", "", True, ("", ""), id="none-none-separate"),
        pytest.param("", "", False, ("", ""), id="none-none-combine"),
        pytest.param("", "", None, ("", ""), id="none-none-default"),
    ),
)
def test_split_format(format, default, flag, expected):
    result = fmt.split_format(format, default, flag)

    assert result == expected


def test_register_unit_format(func_registry):
    @fmt.register_unit_format("custom")
    def format_custom(unit, registry, **options):
        # Ensure the registry is correct..
        registry.Unit(unit)
        return "<formatted unit>"

    quantity = 1.0 * func_registry.meter
    assert f"{quantity:g#~custom}" == "1 <formatted unit>"
    assert f"{quantity:custom}" == "1.0 <formatted unit>"

    with pytest.raises(ValueError, match="format 'custom' already exists"):

        @fmt.register_unit_format("custom")
        def format_custom_redefined(unit, registry, **options):
            return "<overwritten>"


class TestFormatUnitCaretFlag:
    """Test that the '^' flag controls whether to use negative powers."""

    @pytest.mark.parametrize(
        ["unit", "format_spec", "expected", "xfail", "info"],
        [
            pytest.param(
                lambda reg: "",
                "C",
                "dimensionless",
                None,
                "basic-dimensionless",
                id="basic-dimensionless",
            ),
            pytest.param(
                lambda reg: "m",
                "W",
                ValueError,
                None,
                "basic-invalid",
                id="basic-invalid",
            ),
            pytest.param(
                lambda reg: reg.second**-1,
                "D",
                "1 / second",
                None,
                "negative-exponent-default-D",
                id="negative-exponent-default-D",
            ),
            pytest.param(
                lambda reg: reg.second**-1,
                "C",
                "1/second",
                None,
                "negative-exponent-default-C",
                id="negative-exponent-default-C",
            ),
            pytest.param(
                lambda reg: reg.second**-1,
                "P",
                "1/second",
                None,
                "negative-exponent-no-caret-P",
                id="negative-exponent-no-caret-P",
            ),
            pytest.param(
                lambda reg: reg.second**-1,
                "~P",
                "1/s",
                None,
                "negative-exponent-no-caret-~P",
                id="negative-exponent-no-caret-~P",
            ),
            pytest.param(
                lambda reg: reg.second**-1,
                "^P",
                "second⁻¹",
                None,
                "negative-exponent-with-caret-P",
                id="negative-exponent-with-caret-P",
            ),
            pytest.param(
                lambda reg: reg.second**-1,
                "~^P",
                "s⁻¹",
                None,
                "negative-exponent-with-caret-~P",
                id="negative-exponent-with-caret-~P",
            ),
            pytest.param(
                lambda reg: reg.second**-1,
                "^C",
                "second**-1",
                None,
                "negative-exponent-with-caret-compact",
                id="negative-exponent-with-caret-compact",
            ),
            pytest.param(
                lambda reg: reg.kilogram**-1 * reg.meter**-2,
                "^P",
                "kilogram⁻¹·meter⁻²",
                None,
                "multiple-negative-exponents-with-caret",
                id="multiple-negative-exponents-with-caret",
            ),
            pytest.param(
                lambda reg: reg.meter**2 * reg.second**-1,
                "^P",
                "meter²·second⁻¹",
                None,
                "mixed-exponents-with-caret",
                id="mixed-exponents-with-caret",
            ),
            pytest.param(
                lambda reg: 5 * reg.second**-1,
                "~^P",
                "5 s⁻¹",
                None,
                "quantity-with-caret-matches-unit",
                id="quantity-with-caret-matches-unit",
            ),
            pytest.param(
                lambda reg: reg.second**-1,
                "^D",
                "second ** -1",
                None,
                "caret-with-default-formatter-D",
                id="caret-with-default-formatter-D",
            ),
            pytest.param(
                lambda reg: reg.second**-1,
                "^",
                "second ** -1",
                None,
                "caret-with-default-formatter-default",
                id="caret-with-default-formatter-default",
            ),
            pytest.param(
                lambda reg: reg.second**-1,
                "^L",
                r"\mathrm{second}^{-1}",
                None,
                "caret-with-latex-formatter",
                id="caret-with-latex-formatter",
            ),
            pytest.param(
                lambda reg: reg.second**-1,
                "^H",
                "second<sup>-1</sup>",
                None,
                "caret-with-html-formatter",
                id="caret-with-html-formatter",
            ),
            pytest.param(
                lambda reg: reg.meter**-1 * reg.second**-2,
                "~P",
                "1/m/s²",
                None,
                "no-caret-ratio-format",
                id="no-caret-ratio-format",
            ),
            pytest.param(
                lambda reg: reg.meter**-1 * reg.second**-2,
                "~^P",
                "m⁻¹·s⁻²",
                None,
                "with-caret-negative-powers",
                id="with-caret-negative-powers",
            ),
        ],
    )
    def test_format_unit_caret_flag(
        self,
        func_registry,
        unit,
        format_spec,
        expected,
        xfail,
        info,
    ):
        if xfail:
            pytest.xfail(xfail)

        actual_unit = unit(func_registry) if callable(unit) else unit

        if isinstance(actual_unit, str):
            if expected is ValueError:
                with pytest.raises(expected):
                    fmt.format_unit(actual_unit, format_spec)
                return
            result = fmt.format_unit(actual_unit, format_spec)
        else:
            result = f"{actual_unit:{format_spec}}"

        assert result == expected


class TestFormatQuantityConsistency:
    """Ensure quantities and units format consistently with '^' flag."""

    def test_quantity_unit_format_consistency_with_caret(self, func_registry):
        """Test that quantities maintain consistency with standalone units."""
        specs = ["~^P", "~^D", "~^C"]
        u = func_registry.meter**-1 / func_registry.second
        q = 42 * u

        for spec in specs:
            unit_fmt = f"{u:{spec}}"
            quantity_fmt = f"{q:{spec}}"
            # Quantity format should be magnitude + unit format
            assert quantity_fmt.endswith(unit_fmt)

    def test_caret_preserves_quantity_magnitude(self, func_registry):
        """Test that '^' doesn't affect magnitude formatting in quantities."""
        u = func_registry.second**-1
        q = 5.5 * u

        # Magnitude should be identical
        assert f"{q:~^P}".split()[0] == "5.5"
        # Only unit part differs between with/without '^'
        assert f"{q:~P}" == "5.5 1/s"
        assert f"{q:~^P}" == "5.5 s⁻¹"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
