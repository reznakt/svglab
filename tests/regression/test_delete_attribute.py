from svglab import G, Length, Rect, parse_svg


def test_deleted_attribute_reads_as_none() -> None:
    rect = Rect(stroke_width=Length(2))

    del rect.stroke_width

    assert rect.stroke_width is None
    assert "stroke_width" not in rect.model_fields_set
    assert rect.to_xml() == "<rect/>"


def test_deleted_attribute_does_not_break_reify() -> None:
    svg = parse_svg("""
        <svg>
            <g transform="scale(2)">
                <rect width="10" height="10" stroke-width="1"/>
            </g>
        </svg>
    """)
    rect = svg.find(Rect)
    del rect.stroke_width

    svg.reify()

    assert rect.width == Length(20)
    assert svg.find(G).transform is None
    assert rect.transform is None
