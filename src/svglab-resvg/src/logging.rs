use std::cell::RefCell;

use log::{Level, LevelFilter, Log, Metadata, Record};
use pyo3::prelude::*;

struct Captured {
    level: Level,
    target: String,
    message: String,
    file: Option<String>,
    line: Option<u32>,
}

thread_local! {
    static CAPTURED: RefCell<Option<Vec<Captured>>> = const { RefCell::new(None) };
}

/// Forwards records to Python logging, except those logged inside `detach`, which it holds on
/// to until the GIL is back.
struct Logger(pyo3_log::Logger);

impl Log for Logger {
    fn enabled(&self, metadata: &Metadata<'_>) -> bool {
        self.0.enabled(metadata)
    }

    fn log(&self, record: &Record<'_>) {
        if !self.0.enabled(record.metadata()) {
            return;
        }

        let captured = CAPTURED.with_borrow_mut(|captured| {
            captured.as_mut().map(|records| {
                records.push(Captured {
                    level: record.level(),
                    target: record.target().to_owned(),
                    message: record.args().to_string(),
                    file: record.file().map(str::to_owned),
                    line: record.line(),
                });
            })
        });

        if captured.is_none() {
            self.0.log(record);
        }
    }

    fn flush(&self) {}
}

pub(crate) fn init(py: Python<'_>) -> PyResult<()> {
    let logger = pyo3_log::Logger::new(py, pyo3_log::Caching::LoggersAndLevels)?;

    // the same maximum level that `pyo3_log::init` sets
    if log::set_boxed_logger(Box::new(Logger(logger))).is_ok() {
        log::set_max_level(LevelFilter::Debug);
    }

    Ok(())
}

fn replay(records: Vec<Captured>) {
    let logger = log::logger();

    for record in records {
        logger.log(
            &Record::builder()
                .args(format_args!("{}", record.message))
                .level(record.level)
                .target(&record.target)
                .file(record.file.as_deref())
                .line(record.line)
                .build(),
        );
    }
}

/// Hands over what was captured if the closure in `detach` panics.
struct Capture;

impl Drop for Capture {
    fn drop(&mut self) {
        if let Some(records) = CAPTURED.take() {
            replay(records);
        }
    }
}

/// Runs `f` without the GIL, like `Python::detach`, but replays what it logs only once the GIL
/// is reacquired. Forwarding a record needs the GIL, and waiting for it once per record can
/// stall a render for as long as other threads keep it.
pub(crate) fn detach<T, F>(py: Python<'_>, f: F) -> T
where
    T: Send,
    F: Send + FnOnce() -> T,
{
    let (result, records) = py.detach(|| {
        CAPTURED.set(Some(Vec::new()));
        let capture = Capture;

        let result = f();
        let records = CAPTURED.take().unwrap_or_default();
        drop(capture);

        (result, records)
    });

    replay(records);

    result
}
