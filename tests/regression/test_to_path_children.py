from svglab import Desc, G, Length, RawText, Rect, Title


def test_to_path_keeps_the_children() -> None:
    rect = Rect(width=Length(10), height=Length(20))
    rect.add_child(Title().add_child(RawText("a rectangle")))

    path = rect.to_path()
    title = path.find(Title)

    # the children used to be dropped, because they are held in a private
    # attribute rather than in a model field
    assert title.parent is path
    assert title.to_xml() == rect.find(Title).to_xml()


def test_to_path_copies_rather_than_moves_the_children() -> None:
    rect = Rect(width=Length(10), height=Length(20))
    title = Title()
    rect.add_child(title)

    path = rect.to_path()

    assert path.find(Title) is not title
    assert title.parent is rect


def test_to_path_of_a_child_element_stays_detached() -> None:
    rect = Rect(width=Length(10), height=Length(20))
    rect.add_child(Desc())
    group = G().add_child(rect)

    path = rect.to_path()

    assert path.parent is None
    assert list(group.children) == [rect]
