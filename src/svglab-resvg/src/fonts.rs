use std::path::PathBuf;
use std::sync::{Arc, OnceLock};

use resvg::usvg::fontdb;

use crate::errors::Error;

fn system_fonts() -> &'static Arc<fontdb::Database> {
    static SYSTEM_FONTS: OnceLock<Arc<fontdb::Database>> = OnceLock::new();

    SYSTEM_FONTS.get_or_init(|| {
        let mut fonts = fontdb::Database::new();
        fonts.load_system_fonts();

        Arc::new(fonts)
    })
}

pub(crate) fn build_fonts(
    skip_system_fonts: bool,
    font_files: Vec<PathBuf>,
    font_dirs: Vec<PathBuf>,
    cursive_family: Option<String>,
    fantasy_family: Option<String>,
    monospace_family: Option<String>,
    sans_serif_family: Option<String>,
    serif_family: Option<String>,
) -> Result<Arc<fontdb::Database>, Error> {
    let generic_families = [
        &cursive_family,
        &fantasy_family,
        &monospace_family,
        &sans_serif_family,
        &serif_family,
    ];

    let mut fonts = if skip_system_fonts {
        Arc::new(fontdb::Database::new())
    } else {
        Arc::clone(system_fonts())
    };

    if font_files.is_empty()
        && font_dirs.is_empty()
        && generic_families.iter().all(|family| family.is_none())
    {
        return Ok(fonts);
    }

    let database = Arc::make_mut(&mut fonts);

    for file in font_files {
        database.load_font_file(&file).map_err(|error| {
            Error::Io(std::io::Error::new(
                error.kind(),
                format!("cannot load font file {}: {error}", file.display()),
            ))
        })?;
    }

    for dir in font_dirs {
        database.load_fonts_dir(dir);
    }

    if let Some(family) = cursive_family {
        database.set_cursive_family(family);
    }

    if let Some(family) = fantasy_family {
        database.set_fantasy_family(family);
    }

    if let Some(family) = monospace_family {
        database.set_monospace_family(family);
    }

    if let Some(family) = sans_serif_family {
        database.set_sans_serif_family(family);
    }

    if let Some(family) = serif_family {
        database.set_serif_family(family);
    }

    Ok(fonts)
}
