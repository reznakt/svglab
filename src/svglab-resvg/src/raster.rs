use resvg::{tiny_skia, usvg};

use crate::errors::Error;

fn allocate_pixmap(size: tiny_skia::IntSize) -> Result<tiny_skia::Pixmap, Error> {
    let too_large = || {
        Error::Memory(format!(
            "cannot allocate a {}x{} image",
            size.width(),
            size.height()
        ))
    };

    let len = usize::try_from(size.width())
        .ok()
        .and_then(|width| width.checked_mul(usize::try_from(size.height()).ok()?))
        .and_then(|pixels| pixels.checked_mul(tiny_skia::BYTES_PER_PIXEL))
        .ok_or_else(too_large)?;

    let mut probe = Vec::<u8>::new();
    probe.try_reserve_exact(len).map_err(|_| too_large())?;
    drop(probe);

    tiny_skia::Pixmap::from_vec(vec![0; len], size).ok_or_else(too_large)
}

pub(crate) fn rasterize(
    svg: &str,
    options: &usvg::Options<'_>,
    background: Option<(u8, u8, u8, u8)>,
    zoom: f32,
) -> Result<(u32, u32, Vec<u8>), Error> {
    if !zoom.is_finite() || zoom <= 0.0 {
        return Err(Error::Value(format!(
            "zoom must be positive and finite: {zoom}"
        )));
    }

    let tree = usvg::Tree::from_str(svg, options)
        .map_err(|error| Error::Render(format!("cannot parse SVG: {error}")))?;

    let size = tree
        .size()
        .scale_by(zoom)
        .ok_or_else(|| Error::Render(format!("invalid image size: {:?}", tree.size())))?
        .to_int_size();

    let mut pixmap = allocate_pixmap(size)?;

    if let Some((red, green, blue, alpha)) = background {
        pixmap.fill(tiny_skia::Color::from_rgba8(red, green, blue, alpha));
    }

    resvg::render(
        &tree,
        tiny_skia::Transform::from_scale(zoom, zoom),
        &mut pixmap.as_mut(),
    );

    Ok((pixmap.width(), pixmap.height(), pixmap.take_demultiplied()))
}
