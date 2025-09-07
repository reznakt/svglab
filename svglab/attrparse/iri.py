"""Definitions of the <IRI> and <FuncIRI> types."""

from __future__ import annotations

import functools

import pydantic
import rfc3986
from typing_extensions import Annotated, Self, TypeAlias, final, override

from svglab import models, protocols


@pydantic.dataclasses.dataclass(
    frozen=True, kw_only=True, config=models.DATACLASS_CONFIG
)
class Iri(protocols.CustomSerializable):
    """Represents the SVG `<IRI>` type.

    The <IRI> type is a string that represents an Internationalized Resource
    Identifier (IRI). An IRI is a generalization of a URL that allows for
    characters outside the ASCII range.

    """

    scheme: str | None = None
    """The scheme of the IRI, e.g. 'http', 'https', 'ftp', etc."""

    authority: str | None = None
    """The authority of the IRI, e.g. 'www.example.com' or 'example.com'."""

    path: str | None = None
    """The path on the server, e.g. '/path/to/resource'."""

    query: str | None = None
    """The query string of the IRI, e.g. '?key=value&key2=value2'."""

    fragment: str | None = None
    """The fragment identifier of the IRI, e.g. '#section1'."""

    @functools.cached_property
    def is_local(self) -> bool:
        """Whether this is a local IRI reference.

        An IRI is considered local if it has a fragment identifier and no
        scheme, authority, path, or query.

        This is useful for identifying references to elements within the same
        document, for example, when using `url(#id)` in `fill` or `stroke`
        attributes.
        """
        match self:
            case Iri(
                scheme=None,
                authority=None,
                path=None,
                query=None,
                fragment=fragment,
            ) if fragment is not None:
                return True
            case _:
                return False

    @functools.cached_property
    def iri(self) -> str:
        """The full IRI as a string."""
        iri = rfc3986.IRIReference(
            scheme=self.scheme,
            authority=self.authority,
            path=self.path,
            query=self.query,
            fragment=self.fragment,
        )

        return iri.unsplit()

    def to_func_iri(self) -> FuncIri:
        """Convert this Iri to a FuncIri."""
        return FuncIri(
            scheme=self.scheme,
            authority=self.authority,
            path=self.path,
            query=self.query,
            fragment=self.fragment,
        )

    @override
    def serialize(self) -> str:
        return self.iri

    @classmethod
    def from_str(cls, iri: str, /) -> Self:
        """Parse an IRI from a string.

        Args:
            iri: The IRI string to parse. For example 'http://example.com'.

        Returns:
            An instance of the Iri class with the parsed components.

        Raises:
            ValueError: If the IRI is invalid.

        """
        try:
            parsed = rfc3986.iri_reference(iri)

            return cls(
                scheme=parsed.scheme,
                authority=parsed.authority,
                path=parsed.path,
                query=parsed.query,
                fragment=parsed.fragment,
            )

        except Exception as e:
            msg = f"Invalid IRI: {iri}"
            raise ValueError(msg) from e


@final
@pydantic.dataclasses.dataclass(
    frozen=True, config=models.DATACLASS_CONFIG
)
class FuncIri(Iri):
    """Represents the SVG `<FuncIRI>` type.

    <FuncIRI> represents the functional notation for an IRI. The format is
    `url(<IRI>)`, where `<IRI>` is an IRI.
    """

    @functools.cached_property
    def func_iri(self) -> str:
        """The full functional IRI as a string."""
        return f"url({self.iri})"

    def to_iri(self) -> Iri:
        """Convert this FuncIri to an Iri."""
        return Iri(
            scheme=self.scheme,
            authority=self.authority,
            path=self.path,
            query=self.query,
            fragment=self.fragment,
        )

    @override
    def serialize(self) -> str:
        return self.func_iri

    @classmethod
    @override
    def from_str(cls, iri: str, /) -> Self:
        if not iri.startswith("url(") or not iri.endswith(")"):
            msg = f"Invalid FuncIri: {iri}"
            raise ValueError(msg)

        # Remove the url() part
        iri = iri[4:-1].strip()

        return super().from_str(iri)


IriType: TypeAlias = Annotated[
    Iri,
    pydantic.BeforeValidator(
        lambda v: Iri.from_str(v) if isinstance(v, str) else v
    ),
]
FuncIriType: TypeAlias = Annotated[
    FuncIri,
    pydantic.BeforeValidator(
        lambda v: FuncIri.from_str(v) if isinstance(v, str) else v
    ),
]
