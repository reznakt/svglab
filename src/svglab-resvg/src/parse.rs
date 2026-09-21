use resvg::usvg;

use crate::errors::Error;

pub(crate) fn parse_shape_rendering(value: &str) -> Result<usvg::ShapeRendering, Error> {
    match value {
        "optimizeSpeed" => Ok(usvg::ShapeRendering::OptimizeSpeed),
        "crispEdges" => Ok(usvg::ShapeRendering::CrispEdges),
        "geometricPrecision" => Ok(usvg::ShapeRendering::GeometricPrecision),
        _ => Err(Error::Value(format!("invalid shape_rendering: {value:?}"))),
    }
}

pub(crate) fn parse_text_rendering(value: &str) -> Result<usvg::TextRendering, Error> {
    match value {
        "optimizeSpeed" => Ok(usvg::TextRendering::OptimizeSpeed),
        "optimizeLegibility" => Ok(usvg::TextRendering::OptimizeLegibility),
        "geometricPrecision" => Ok(usvg::TextRendering::GeometricPrecision),
        _ => Err(Error::Value(format!("invalid text_rendering: {value:?}"))),
    }
}

pub(crate) fn parse_image_rendering(value: &str) -> Result<usvg::ImageRendering, Error> {
    match value {
        "optimizeQuality" => Ok(usvg::ImageRendering::OptimizeQuality),
        "optimizeSpeed" => Ok(usvg::ImageRendering::OptimizeSpeed),
        _ => Err(Error::Value(format!("invalid image_rendering: {value:?}"))),
    }
}
