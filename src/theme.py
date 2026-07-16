"""SkySpotter color palette: cool blue chrome for aviation culling.

Keep token names aligned with upstream RAWviewer (`theme.py`) so Adjust /
gallery / chrome call sites stay portable, but remap the palette to SkySpotter
blue rather than the warm darkroom / EMBER orange look.

- SKY (exported as EMBER) is the single "active" accent: selection ring, armed
  tool, dragged slider.
- DODGE marks decided status (star rating, bookmark, edited badge).
- HIST_* stay true channel colors for histogram / clipping overlays.
"""

VOID = "#0f1419"
SURFACE = "#151c24"
RAISED = "#1c2630"
RAISED_HI = "#243140"
LINE = "#2e3d4d"
LINE_SOFT = "#1f2a36"
INK = "#e8eef5"
INK_MUTED = "#8fa3b8"
INK_FAINT = "#5c7085"

# Active accent — sky blue (token kept as EMBER for upstream compatibility)
EMBER = "#4A9EFF"
EMBER_DIM = "rgba(74, 158, 255, 0.28)"
EMBER_GLOW = "rgba(74, 158, 255, 0.45)"

DODGE = "#5CB8FF"
BURN = "#3d6f99"

HIST_R = "#e5484d"
HIST_G = "#3dd68c"
HIST_B = "#4a9eff"

# Integer-tuple equivalents for QColor(r, g, b[, a]) call sites.
VOID_RGB = (15, 20, 25)
SURFACE_RGB = (21, 28, 36)
RAISED_RGB = (28, 38, 48)
RAISED_HI_RGB = (36, 49, 64)
LINE_RGB = (46, 61, 77)
LINE_SOFT_RGB = (31, 42, 54)
INK_RGB = (232, 238, 245)
INK_MUTED_RGB = (143, 163, 184)
INK_FAINT_RGB = (92, 112, 133)
EMBER_RGB = (74, 158, 255)
DODGE_RGB = (92, 184, 255)
BURN_RGB = (61, 111, 153)
HIST_R_RGB = (229, 72, 77)
HIST_G_RGB = (61, 214, 140)
HIST_B_RGB = (74, 158, 255)


def rgba(rgb: tuple[int, int, int], alpha: int) -> str:
    """QSS/QColor-style rgba() string from one of the *_RGB tuples above."""
    r, g, b = rgb
    return f"rgba({r}, {g}, {b}, {alpha})"
