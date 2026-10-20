from svglab import Iri, Rect, Use, parse_svg


def test_non_ascii_fragment_is_kept_verbatim() -> None:
    iri = Iri.from_str("#vrstva_č1")

    assert iri.fragment == "vrstva_č1"
    assert iri.serialize() == "#vrstva_č1"


def test_non_ascii_fragment_resolves() -> None:
    svg = parse_svg("""
        <svg>
            <rect id="gř"/>
            <use href="#gř"/>
        </svg>
    """)
    use = svg.find(Use)

    assert use.href is not None
    assert svg.resolve_iri(use.href) is svg.find(Rect)
    assert 'href="#gř"' in use.to_xml()
