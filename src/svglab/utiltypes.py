"""Utility types that should be defined globally."""

import numpy as np
import numpy.typing as npt
from typing_extensions import Literal, TypeAlias


Xmlns: TypeAlias = Literal["http://www.w3.org/2000/svg"]
"""Type representing valid values for the `xmlns` attribute."""

NpFloat: TypeAlias = np.float64
"""The floating-point type used for numpy arrays."""

NpFloatArray: TypeAlias = npt.NDArray[NpFloat]
"""An ndarray of floating-point numbers."""

LengthUnit: TypeAlias = (
    Literal[
        "%",
        "ch",
        "cm",
        "em",
        "ex",
        "in",
        "mm",
        "pc",
        "pt",
        "px",
        "Q",
        "rem",
        "vh",
        "vmax",
        "vmin",
        "vw",
    ]
    | None
)
"""Units of `<length>`."""
