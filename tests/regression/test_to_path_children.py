import svglab


def test_to_path_keeps_the_children() -> None:
    rect = svglab.Rect(width=svglab.Length(10), height=svglab.Length(20))
    rect.add_child(svglab.Title().add_child(svglab.RawText("a rectangle")))

    path = rect.to_path()
    title = path.find(svglab.Title)

    # the children used to be dropped, because they are held in a private
    # attribute rather than in a model field
    assert title.parent is path
    assert title.to_xml() == rect.find(svglab.Title).to_xml()


def test_to_path_copies_rather_than_moves_the_children() -> None:
    rect = svglab.Rect(width=svglab.Length(10), height=svglab.Length(20))
    title = svglab.Title()
    rect.add_child(title)

    path = rect.to_path()

    assert path.find(svglab.Title) is not title
    assert title.parent is rect


def test_to_path_of_a_child_element_stays_detached() -> None:
    rect = svglab.Rect(width=svglab.Length(10), height=svglab.Length(20))
    rect.add_child(svglab.Desc())
    group = svglab.G().add_child(rect)

    path = rect.to_path()

    assert path.parent is None
    assert list(group.children) == [rect]
