use std::str::FromStr;

use crate::errors::Error;

pub(crate) fn parse<T: FromStr>(name: &str, value: &str) -> Result<T, Error> {
    value
        .parse()
        .map_err(|_| Error::Value(format!("invalid {name}: {value:?}")))
}
