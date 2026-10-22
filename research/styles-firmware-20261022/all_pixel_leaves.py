"""Available independent set models; separate whites curve is always explicit."""
import pixel_leaves
import pixel_tonal
import pixel_lighten
import pixel_color
import pixel_remaining


def models(whites_curve=None):
    return {**pixel_leaves.models(whites_curve),**pixel_tonal.models(),**pixel_lighten.models(),**pixel_color.models(),**pixel_remaining.models()}
