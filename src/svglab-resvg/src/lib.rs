mod errors;
mod fonts;
mod parse;
mod raster;

use std::path::PathBuf;

use pyo3::prelude::*;
use pyo3::types::PyBytes;
use pyo3::wrap_pyfunction;
use resvg::usvg;

use crate::errors::{Error, RenderError};
use crate::fonts::{FontOptions, build_fonts, default_family};
use crate::parse::{parse_image_rendering, parse_shape_rendering, parse_text_rendering};
use crate::raster::rasterize;

/// Render an SVG document into unpremultiplied RGBA pixels.
#[pyfunction]
#[pyo3(signature = (
    svg,
    *,
    background,
    cursive_family,
    default_size,
    dpi,
    fantasy_family,
    font_dirs,
    font_family,
    font_files,
    font_size,
    image_rendering,
    languages,
    monospace_family,
    resources_dir,
    sans_serif_family,
    serif_family,
    shape_rendering,
    skip_system_fonts,
    style_sheet,
    text_rendering,
    zoom,
))]
fn render(
    py: Python<'_>,
    svg: String,
    background: Option<(u8, u8, u8, u8)>,
    cursive_family: Option<String>,
    default_size: (f32, f32),
    dpi: f32,
    fantasy_family: Option<String>,
    font_dirs: Vec<PathBuf>,
    font_family: Option<String>,
    font_files: Vec<PathBuf>,
    font_size: f32,
    image_rendering: &str,
    languages: Vec<String>,
    monospace_family: Option<String>,
    resources_dir: Option<PathBuf>,
    sans_serif_family: Option<String>,
    serif_family: Option<String>,
    shape_rendering: &str,
    skip_system_fonts: bool,
    style_sheet: Option<String>,
    text_rendering: &str,
    zoom: f32,
) -> PyResult<(u32, u32, Py<PyBytes>)> {
    let (width, height) = default_size;

    let default_size = usvg::Size::from_wh(width, height)
        .ok_or_else(|| Error::Value(format!("invalid default_size: {width}x{height}")))?;

    let image_rendering = parse_image_rendering(image_rendering)?;
    let shape_rendering = parse_shape_rendering(shape_rendering)?;
    let text_rendering = parse_text_rendering(text_rendering)?;

    let font_options = FontOptions {
        cursive_family,
        fantasy_family,
        font_dirs,
        font_files,
        monospace_family,
        sans_serif_family,
        serif_family,
        skip_system_fonts,
    };

    let (width, height, pixels) = py.detach(move || {
        let serif_is_chosen = font_options.serif_family.is_some();
        let fonts = build_fonts(&font_options)?;
        let font_family = font_family.unwrap_or_else(|| default_family(&fonts, serif_is_chosen));

        let options = usvg::Options {
            default_size,
            dpi,
            font_family,
            font_size,
            fontdb: fonts,
            image_rendering,
            languages,
            resources_dir,
            shape_rendering,
            style_sheet,
            text_rendering,
            ..usvg::Options::default()
        };

        rasterize(&svg, &options, background, zoom)
    })?;

    Ok((width, height, PyBytes::new(py, &pixels).unbind()))
}

#[pymodule]
fn _resvg(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let _ = pyo3_log::try_init();

    module.add("RenderError", module.py().get_type::<RenderError>())?;
    module.add(
        "PanicError",
        module.py().get_type::<pyo3::panic::PanicException>(),
    )?;

    module.add_function(wrap_pyfunction!(render, module)?)?;

    Ok(())
}
