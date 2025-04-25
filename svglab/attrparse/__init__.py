"""Definitions and parsing of SVG attribute types.

This package provides classes to represent SVG attribute types that cannot be
parsed directly by Pydantic, such as `<transform-list>`, `<list-of-points>`,
`<color>`, and `<length>`.

It also provides logic to parse strings into these types and include them in
Pydantic models.
"""
