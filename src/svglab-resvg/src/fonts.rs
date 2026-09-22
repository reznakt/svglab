use std::path::PathBuf;
use std::sync::{Arc, Mutex, OnceLock};

use resvg::usvg::fontdb;

use crate::errors::Error;

#[derive(Clone, PartialEq, Eq)]
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
        self.font_files.is_empty()
            && self.font_dirs.is_empty()
            && self.cursive_family.is_none()
            && self.fantasy_family.is_none()
            && self.monospace_family.is_none()
            && self.sans_serif_family.is_none()
            && self.serif_family.is_none()
    }
}

fn system_fonts() -> &'static Arc<fontdb::Database> {
    static SYSTEM_FONTS: OnceLock<Arc<fontdb::Database>> = OnceLock::new();

    SYSTEM_FONTS.get_or_init(|| {
        let mut fonts = fontdb::Database::new();
        fonts.load_system_fonts();

        Arc::new(fonts)
    })
}

type DerivedFonts = Mutex<Option<(FontOptions, Arc<fontdb::Database>)>>;

fn derived_fonts() -> &'static DerivedFonts {
    static DERIVED_FONTS: OnceLock<DerivedFonts> = OnceLock::new();

    DERIVED_FONTS.get_or_init(|| Mutex::new(None))
}

fn load_fonts(options: &FontOptions) -> Result<Arc<fontdb::Database>, Error> {
    let mut database = if options.skip_system_fonts {
        fontdb::Database::new()
    } else {
        (**system_fonts()).clone()
    };

    for file in &options.font_files {
        database.load_font_file(file).map_err(|source| Error::Io {
            path: file.clone(),
            source,
        })?;
    }

    for dir in &options.font_dirs {
        database.load_fonts_dir(dir);
    }

    if let Some(family) = &options.cursive_family {
        database.set_cursive_family(family.clone());
    }

    if let Some(family) = &options.fantasy_family {
        database.set_fantasy_family(family.clone());
    }

    if let Some(family) = &options.monospace_family {
        database.set_monospace_family(family.clone());
    }

    if let Some(family) = &options.sans_serif_family {
        database.set_sans_serif_family(family.clone());
    }

    if let Some(family) = &options.serif_family {
        database.set_serif_family(family.clone());
    }

    Ok(Arc::new(database))
}

pub(crate) fn build_fonts(options: &FontOptions) -> Result<Arc<fontdb::Database>, Error> {
    if options.is_bare() {
        return Ok(if options.skip_system_fonts {
            Arc::new(fontdb::Database::new())
        } else {
            Arc::clone(system_fonts())
        });
    }

    let cache = derived_fonts();

    let hit = cache.lock().ok().and_then(|cached| match cached.as_ref() {
        Some((key, fonts)) if key == options => Some(Arc::clone(fonts)),
        _ => None,
    });

    if let Some(fonts) = hit {
        return Ok(fonts);
    }

    let fonts = load_fonts(options)?;

    if let Ok(mut cached) = cache.lock() {
        *cached = Some((options.clone(), Arc::clone(&fonts)));
    }

    Ok(fonts)
}

pub(crate) fn default_family(fonts: &fontdb::Database, serif_is_chosen: bool) -> String {
    let serif = fonts.family_name(&fontdb::Family::Serif);

    if serif_is_chosen {
        return serif.to_owned();
    }

    let query = fontdb::Query {
        families: &[fontdb::Family::Serif],
        weight: fontdb::Weight::NORMAL,
        stretch: fontdb::Stretch::Normal,
        style: fontdb::Style::Normal,
    };

    if fonts.query(&query).is_some() {
        return serif.to_owned();
    }

    fonts
        .faces()
        .find_map(|face| face.families.first().map(|(name, _)| name.clone()))
        .unwrap_or_else(|| serif.to_owned())
}
