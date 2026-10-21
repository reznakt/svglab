import inspect

import svglab
from svglab import errors


def test_every_error_is_exported() -> None:
    error_names = {
        name
        for name, value in vars(errors).items()
        if inspect.isclass(value) and issubclass(value, errors.SvgError)
    }

    assert error_names <= set(svglab.__all__)
