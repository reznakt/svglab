use std::ffi::c_int;

use pyo3::ffi;
use pyo3::prelude::*;

/// Rendered pixels, which Pillow maps through the buffer protocol instead of copying them.
#[pyclass(frozen, module = "_resvg")]
pub(crate) struct Pixels {
    /// The width of the image, in pixels.
    #[pyo3(get)]
    width: u32,
    /// The height of the image, in pixels.
    #[pyo3(get)]
    height: u32,
    data: Vec<u8>,
}

impl Pixels {
    pub(crate) fn new(width: u32, height: u32, data: Vec<u8>) -> Self {
        Self {
            width,
            height,
            data,
        }
    }
}

#[pymethods]
impl Pixels {
    #[expect(unsafe_code, reason = "pyo3 has no safe way to export a buffer")]
    unsafe fn __getbuffer__(
        slf: &Bound<'_, Self>,
        view: *mut ffi::Py_buffer,
        flags: c_int,
    ) -> PyResult<()> {
        let data = &slf.get().data;
        let len = ffi::Py_ssize_t::try_from(data.len())?;

        // SAFETY: `view` comes from the interpreter, and the reference to `slf` that
        // `PyBuffer_FillInfo` stores in it keeps `data` alive; the buffer is exported read-only
        // and `data` is never changed.
        let status = unsafe {
            ffi::PyBuffer_FillInfo(
                view,
                slf.as_ptr(),
                data.as_ptr().cast_mut().cast(),
                len,
                1,
                flags,
            )
        };

        if status == -1 {
            return Err(PyErr::fetch(slf.py()));
        }

        Ok(())
    }
}
