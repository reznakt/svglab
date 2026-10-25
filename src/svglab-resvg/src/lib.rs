mod errors;
mod fonts;
mod logging;
mod pixels;
mod raster;

use std::path::PathBuf;
use std::str::FromStr;

use pyo3::prelude::*;
use resvg::usvg;

use crate::errors::Error;
use crate::fonts::{DEFAULT_FAMILY, FontOptions, build_fonts};
use crate::pixels::Pixels;
use crate::raster::rasterize;

fn parse<T: FromStr>(value: &Bound<'_, PyAny>) -> PyResult<T> {
    let value: &str = value.extract()?;

    value
        .parse()
        .map_err(|_| Error::Value(format!("invalid value: {value:?}")).into())
}

/// The settings of a `RenderOptions` other than the font ones, read from its attributes of the
/// same names.
#[derive(FromPyObject)]
struct Settings {
    default_size: (f32, f32),
    dpi: f32,
    font_family: Option<String>,
    font_size: f32,
    #[pyo3(from_py_with = parse)]
    image_rendering: usvg::ImageRendering,
    languages: Vec<String>,
    resources_dir: Option<PathBuf>,
    #[pyo3(from_py_with = parse)]
    shape_rendering: usvg::ShapeRendering,
    style_sheet: Option<String>,
    #[pyo3(from_py_with = parse)]
    text_rendering: usvg::TextRendering,
}

/// Render an SVG document into unpremultiplied RGBA pixels.
#[pyfunction]
#[pyo3(signature = (svg, options, /, *, background, zoom))]
fn render(
    py: Python<'_>,
    svg: String,
    options: &Bound<'_, PyAny>,
    background: Option<(u8, u8, u8, u8)>,
    zoom: f32,
) -> PyResult<Pixels> {
    let font_options: FontOptions = options.extract()?;
    let settings: Settings = options.extract()?;
    let (width, height) = settings.default_size;

    let default_size = usvg::Size::from_wh(width, height)
        .ok_or_else(|| Error::Value(format!("invalid default_size: {width}x{height}")))?;

    let pixels = logging::detach(py, move || {
        let (fonts, font_resolver) = build_fonts(&font_options)?;

        let options = usvg::Options {
            default_size,
            dpi: settings.dpi,
            font_family: settings
                .font_family
                .unwrap_or_else(|| DEFAULT_FAMILY.to_owned()),
            font_resolver,
            font_size: settings.font_size,
            fontdb: fonts,
            image_rendering: settings.image_rendering,
            languages: settings.languages,
            resources_dir: settings.resources_dir,
            shape_rendering: settings.shape_rendering,
            style_sheet: settings.style_sheet,
            text_rendering: settings.text_rendering,
            ..usvg::Options::default()
        };

        rasterize(&svg, &options, background, zoom)
    })?;

    Ok(pixels)
}

#[pymodule]
mod _resvg {
    use pyo3::prelude::*;

    #[pymodule_export]
    use super::render;
    #[pymodule_export]
    use crate::errors::RenderError;
    #[pymodule_export]
    use crate::pixels::Pixels;

    #[pymodule_init]
    fn init(module: &Bound<'_, PyModule>) -> PyResult<()> {
        crate::logging::init(module.py())?;

        module.add(
            "PanicError",
            module.py().get_type::<pyo3::panic::PanicException>(),
        )
    }
}
