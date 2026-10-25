use std::sync::LazyLock;

use resvg::{tiny_skia, usvg};

use crate::errors::Error;
use crate::pixels::Pixels;

/// What `Pixmap::take_demultiplied` turns each channel value into under each alpha, indexed by
/// alpha and then by channel. It is taken from tiny-skia itself, so a lookup gives exactly what
/// it would, rounding included.
static DEMULTIPLIED: LazyLock<Box<[[u8; 256]; 256]>> = LazyLock::new(|| {
    let data = (0..=u8::MAX)
        .flat_map(|alpha| (0..=u8::MAX).flat_map(move |channel| [channel, channel, channel, alpha]))
        .collect();

    let size = tiny_skia::IntSize::from_wh(256, 256).expect("256x256 is a valid size");
    let pixmap = tiny_skia::Pixmap::from_vec(data, size).expect("the data fills the pixmap");
    let demultiplied = pixmap.take_demultiplied();
    let (pixels, _) = demultiplied.as_chunks::<{ tiny_skia::BYTES_PER_PIXEL }>();
    let (rows, _) = pixels.as_chunks::<256>();

    // row by row, so that the 64 KiB table never sits on a possibly small thread stack
    let table: Box<[[u8; 256]]> = rows
        .iter()
        .map(|row| std::array::from_fn(|channel| row[channel][0]))
        .collect();

    table.try_into().expect("there is a row for every alpha")
});

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

/// `Pixmap::take_demultiplied`, but by table lookup instead of three `f64` divisions per pixel.
fn take_demultiplied(pixmap: tiny_skia::Pixmap) -> Vec<u8> {
    let table = &**DEMULTIPLIED;
    let mut data = pixmap.take();

    // Opaque pixels demultiply to themselves and transparent ones are all zeros, so a mostly
    // empty image is only read, and the pages it never drew on stay unallocated.
    #[expect(
        clippy::chunks_exact_to_as_chunks,
        reason = "as_chunks_mut makes this loop twice as slow on opaque pixels"
    )]
    for pixel in data.chunks_exact_mut(tiny_skia::BYTES_PER_PIXEL) {
        let alpha = pixel[3];

        if alpha != 0 && alpha != u8::MAX {
            let row = &table[usize::from(alpha)];

            for channel in &mut pixel[..3] {
                *channel = row[usize::from(*channel)];
            }
        }
    }

    data
}

pub(crate) fn rasterize(
    svg: &str,
    options: &usvg::Options<'_>,
    background: Option<(u8, u8, u8, u8)>,
    zoom: f32,
) -> Result<Pixels, Error> {
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

    Ok(Pixels::new(
        pixmap.width(),
        pixmap.height(),
        take_demultiplied(pixmap),
    ))
}
