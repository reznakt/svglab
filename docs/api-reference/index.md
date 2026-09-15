# API Reference

Generated from the source: every class, method and attribute with its real signature and docstring. For the concepts behind them, start with the [User Guide](../user-guide/index.md).

<div class="grid cards" markdown>

-   :material-shape:{ .lg .middle } __Elements__

    ---

    One page per element class &mdash; all 80 of them, from `Svg` and `G` down to the filter primitives. Pick one from the navigation, or jump to a common shape:

    [`Rect`](elements/Rect.md) &middot;
    [`Circle`](elements/Circle.md) &middot;
    [`Path`](elements/Path.md) &middot;
    [`G`](elements/G.md) &middot;
    [`Svg`](elements/Svg.md)

-   :material-family-tree:{ .lg .middle } __Traits__

    ---

    The element category classes and the methods they contribute:

    [`GraphicsElement`](traits/GraphicsElement.md) &middot;
    [`Shape`](traits/Shape.md) &middot;
    [`BasicShape`](traits/BasicShape.md) &middot;
    [`ContainerElement`](traits/ContainerElement.md)

-   :material-tag-text:{ .lg .middle } __[Attributes](attributes.md)__

    ---

    The single-attribute mixins that define each attribute's type and validation, as one catalogue page.

-   :material-group:{ .lg .middle } __[Attribute Groups](attribute-groups.md)__

    ---

    The fourteen mixin classes that bundle the attributes the specification groups together.

</div>

!!! info "Built in CI"
    These pages are rendered by [mkdocstrings](https://mkdocstrings.github.io/) only when the `CI` environment variable is set, so a local `properdocs build` leaves them empty. Set `CI=true` to render them locally.
