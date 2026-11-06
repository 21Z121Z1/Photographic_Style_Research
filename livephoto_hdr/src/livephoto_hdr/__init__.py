"""Portable Live Photo HDR research baseline.

Native Core Image, Metal, Vision, and CMImaging are not executed here.
"""

NATIVE_BLOCK = {
    "coreImage": "blocked",
    "metal": "blocked",
    "vision": "blocked",
    "cmImagingSPI": "blocked",
    "executed": False,
    "success": False,
    "reason": (
        "This Linux host cannot run Core Image, Metal, Vision, or the private "
        "CMImaging SPI. Hosted macOS runners returned constructor_test.constructed=false "
        "(HANDOFF 4.1). A green availability check is not native execution."
    ),
}
