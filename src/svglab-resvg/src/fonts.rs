use std::path::PathBuf;
use std::sync::{Arc, LazyLock, Mutex, PoisonError};

use resvg::usvg::fontdb;

use crate::errors::Error;

#[derive(Clone, Default, PartialEq, Eq)]
pub(crate) struct FontOptions {
    pub cursive_family: Option<String>,
    pub fantasy_family: Option<String>,
    pub font_dirs: Vec<PathBuf>,
    pub font_files: Vec<PathBuf>,
    pub monospace_family: Option<String>,
    pub sans_serif_family: Option<String>,
    pub serif_family: Option<String>,
    pub skip_system_fonts: bool,
}

impl FontOptions {
    fn is_bare(&self) -> bool {
        *self
            == Self {
                skip_system_fonts: self.skip_system_fonts,
                ..Self::default()
            }
    }
}

/// A generic family, how to point it at a family in a database, and the option that does.
struct GenericFamily {
    family: fontdb::Family<'static>,
    set: fn(&mut fontdb::Database, String),
    chosen: fn(&FontOptions) -> Option<&str>,
}

const GENERIC_FAMILIES: [GenericFamily; 5] = [
    GenericFamily {
        family: fontdb::Family::Cursive,
        set: fontdb::Database::set_cursive_family,
        chosen: |options| options.cursive_family.as_deref(),
    },
    GenericFamily {
        family: fontdb::Family::Fantasy,
        set: fontdb::Database::set_fantasy_family,
        chosen: |options| options.fantasy_family.as_deref(),
    },
    GenericFamily {
        family: fontdb::Family::Monospace,
        set: fontdb::Database::set_monospace_family,
        chosen: |options| options.monospace_family.as_deref(),
    },
    GenericFamily {
        family: fontdb::Family::SansSerif,
        set: fontdb::Database::set_sans_serif_family,
        chosen: |options| options.sans_serif_family.as_deref(),
    },
    GenericFamily {
        family: fontdb::Family::Serif,
        set: fontdb::Database::set_serif_family,
        chosen: |options| options.serif_family.as_deref(),
    },
];

static SYSTEM_FONTS: LazyLock<Arc<fontdb::Database>> = LazyLock::new(|| {
    let mut fonts = fontdb::Database::new();
    fonts.load_system_fonts();
    repair_generic_families(&mut fonts);

    Arc::new(fonts)
});

static DERIVED_FONTS: Mutex<Option<(FontOptions, Arc<fontdb::Database>)>> = Mutex::new(None);

fn is_available(fonts: &fontdb::Database, family: fontdb::Family<'_>) -> bool {
    let query = fontdb::Query {
        families: &[family],
        weight: fontdb::Weight::NORMAL,
        stretch: fontdb::Stretch::Normal,
        style: fontdb::Style::Normal,
    };

    fonts.query(&query).is_some()
}

fn repair_generic_families(fonts: &mut fontdb::Database) {
    let Some(fallback) = fonts
        .faces()
        .find_map(|face| face.families.first().map(|(name, _)| name.clone()))
    else {
        return;
    };

    for generic in &GENERIC_FAMILIES {
        if !is_available(fonts, generic.family) {
            (generic.set)(fonts, fallback.clone());
        }
    }
}

fn load_fonts(options: &FontOptions) -> Result<Arc<fontdb::Database>, Error> {
    let mut fonts = if options.skip_system_fonts {
        fontdb::Database::new()
    } else {
        (**SYSTEM_FONTS).clone()
    };

    for file in &options.font_files {
        fonts.load_font_file(file).map_err(|source| Error::Io {
            path: file.clone(),
            source,
        })?;
    }

    for dir in &options.font_dirs {
        fonts.load_fonts_dir(dir);
    }

    repair_generic_families(&mut fonts);

    for generic in &GENERIC_FAMILIES {
        if let Some(family) = (generic.chosen)(options) {
            (generic.set)(&mut fonts, family.to_owned());
        }
    }

    Ok(Arc::new(fonts))
}

pub(crate) fn build_fonts(options: &FontOptions) -> Result<Arc<fontdb::Database>, Error> {
    if options.is_bare() && !options.skip_system_fonts {
        return Ok(Arc::clone(&SYSTEM_FONTS));
    }

    let mut cached = DERIVED_FONTS.lock().unwrap_or_else(PoisonError::into_inner);

    if let Some((key, fonts)) = cached.as_ref()
        && key == options
    {
        return Ok(Arc::clone(fonts));
    }

    let fonts = load_fonts(options)?;
    *cached = Some((options.clone(), Arc::clone(&fonts)));

    Ok(fonts)
}

pub(crate) fn default_family(fonts: &fontdb::Database) -> String {
    fonts.family_name(&fontdb::Family::Serif).to_owned()
}
