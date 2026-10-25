use std::collections::HashMap;
use std::ops::Deref;
use std::path::PathBuf;
use std::sync::{Arc, LazyLock, Mutex, PoisonError};

use pyo3::FromPyObject;
use resvg::usvg;
use resvg::usvg::fontdb;

use crate::errors::Error;

/// The font settings of a `RenderOptions`, read from its attributes of the same names.
#[derive(Clone, Default, PartialEq, Eq, FromPyObject)]
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

/// The fallback faces already chosen from one database, by character and the faces tried
/// before. usvg asks again for every text chunk that lacks a glyph, and each time it scans the
/// faces until one has it, which is all of them when none does.
type Fallbacks = Mutex<HashMap<(char, Vec<fontdb::ID>), Option<fontdb::ID>>>;

static SYSTEM_FALLBACKS: LazyLock<Fallbacks> = LazyLock::new(Fallbacks::default);

/// The fonts last loaded for options other than the bare defaults.
struct Derived {
    options: FontOptions,
    fonts: Arc<fontdb::Database>,
    fallbacks: Arc<Fallbacks>,
}

static DERIVED_FONTS: Mutex<Option<Derived>> = Mutex::new(None);

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

fn derived_fonts(options: &FontOptions) -> Result<(Arc<fontdb::Database>, Arc<Fallbacks>), Error> {
    let mut cached = DERIVED_FONTS.lock().unwrap_or_else(PoisonError::into_inner);

    if let Some(derived) = cached.as_ref()
        && derived.options == *options
    {
        return Ok((Arc::clone(&derived.fonts), Arc::clone(&derived.fallbacks)));
    }

    let derived = cached.insert(Derived {
        options: options.clone(),
        fonts: load_fonts(options)?,
        fallbacks: Arc::default(),
    });

    Ok((Arc::clone(&derived.fonts), Arc::clone(&derived.fallbacks)))
}

/// usvg's fallback selector, remembering its answers in `fallbacks`, which must belong to the
/// database the selector is handed.
fn select_fallback(
    fallbacks: impl Deref<Target = Fallbacks> + Send + Sync + 'static,
) -> usvg::FallbackSelectionFn<'static> {
    let select_fallback = usvg::FontResolver::default_fallback_selector();

    Box::new(move |c, tried, fonts| {
        let key = (c, tried.to_vec());
        let chosen = fallbacks
            .lock()
            .unwrap_or_else(PoisonError::into_inner)
            .get(&key)
            .copied();

        chosen.unwrap_or_else(|| {
            let id = select_fallback(c, tried, fonts);

            fallbacks
                .lock()
                .unwrap_or_else(PoisonError::into_inner)
                .insert(key, id);

            id
        })
    })
}

/// The font database to render with, and the resolver that picks fonts from it.
///
/// Loading the system fonts takes a while, so when they are all that is asked for, the database
/// starts out empty and the resolver loads them once a document turns out to have text.
pub(crate) fn build_fonts(
    options: &FontOptions,
) -> Result<(Arc<fontdb::Database>, usvg::FontResolver<'static>), Error> {
    if !options.is_bare() || options.skip_system_fonts {
        let (fonts, fallbacks) = derived_fonts(options)?;

        let resolver = usvg::FontResolver {
            select_fallback: select_fallback(fallbacks),
            ..usvg::FontResolver::default()
        };

        return Ok((fonts, resolver));
    }

    let select_font = usvg::FontResolver::default_font_selector();

    let resolver = usvg::FontResolver {
        select_font: Box::new(move |font, fonts| {
            if fonts.is_empty() {
                *fonts = Arc::clone(&SYSTEM_FONTS);
            }

            select_font(font, fonts)
        }),
        // a fallback is only looked for once `select_font` has loaded the system fonts
        select_fallback: select_fallback(LazyLock::force(&SYSTEM_FALLBACKS)),
    };

    Ok((Arc::new(fontdb::Database::new()), resolver))
}

/// The family to fall back on where a document names none. usvg's font selector appends
/// `serif` to every query and no face is called this, so it resolves to whatever `serif`
/// resolves to, without loading the fonts to find out which family that is.
pub(crate) const DEFAULT_FAMILY: &str = "serif";
