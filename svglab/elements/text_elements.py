from typing import final

import bs4
from typing_extensions import override

from svglab.elements import common


@final
class CData(common.TextElement):
    """A `CDATA` section.

    A `CDATA` section is a block of text that is not parsed by the XML parser,
    but is interpreted verbatim.

    `CDATA` sections are used to include text that contains characters
    that would otherwise be interpreted as XML markup.

    Example: `<![CDATA[<g id="foo"></g>]]>`
    """

    def __init__(self, content: str, /) -> None:
        super().__init__(content=content)

    @override
    def to_beautifulsoup_object(self) -> bs4.CData:
        return bs4.CData(self.content)


@final
class Comment(common.TextElement):
    """A comment.

    A comment is a block of text that is not parsed by the XML parser,
    but is ignored.

    Comments are used to include notes and other information that is not
    intended to be displayed to the user.

    Example: `<!-- This is a comment -->`
    """

    def __init__(self, content: str, /) -> None:
        super().__init__(content=content)

    @override
    def to_beautifulsoup_object(self) -> bs4.Comment:
        return bs4.Comment(self.content)


@final
class RawText(common.TextElement):
    """A text node.

    A text node is a block of text that is parsed by the XML parser.

    Text nodes are used to include text that is intended to be displayed
    to the user.

    Example: `Hello, world!`
    """

    def __init__(self, content: str, /) -> None:
        super().__init__(content=content)

    @override
    def to_beautifulsoup_object(self) -> bs4.NavigableString:
        return bs4.NavigableString(self.content)
