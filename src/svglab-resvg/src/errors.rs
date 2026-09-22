use std::path::PathBuf;

use pyo3::PyErr;
use pyo3::create_exception;
use pyo3::exceptions::{PyException, PyMemoryError, PyOSError, PyValueError};

create_exception!(
    _resvg,
    RenderError,
    PyException,
    "Raised when an SVG document cannot be rasterized."
);

#[derive(Debug)]
pub(crate) enum Error {
    Value(String),
    Render(String),
    Io {
        path: PathBuf,
        source: std::io::Error,
    },
    Memory(String),
}

impl From<Error> for PyErr {
    fn from(error: Error) -> Self {
        match error {
            Error::Value(message) => PyValueError::new_err(message),
            Error::Render(message) => RenderError::new_err(message),
            Error::Io { path, source } => match source.raw_os_error() {
                Some(errno) => {
                    PyOSError::new_err((errno, source.to_string(), path.display().to_string()))
                }
                None => std::io::Error::new(source.kind(), format!("{}: {source}", path.display()))
                    .into(),
            },
            Error::Memory(message) => PyMemoryError::new_err(message),
        }
    }
}
