//! Observation ownership: every measured datum enters an evidence set at most once.
//!
//! A SATCOM burst provides `<epoch>.bto`, `<epoch>.bfo` and `<epoch>.<event>` (e.g.
//! `m0019a.logon`), as listed by `satcom::Epoch::observations`. Other data are named
//! `<source>:<item>` by the module that uses them. The prefix names the data source (debris:,
//! image:, search:, acoustic:, radar:), not the module, so two modules that use the same
//! datum collide here. The runner builds one assignment per case (and, with impacts, per
//! evidence set) before anything runs, refuses any overlap, and records it in run.json.

use std::collections::{BTreeMap, BTreeSet};

pub struct Assignment<'a> {
    /// Every SATCOM observation ID the observation table provides.
    known: &'a BTreeSet<String>,
    consumers: BTreeMap<String, String>,
}

impl<'a> Assignment<'a> {
    pub fn new(known: &'a BTreeSet<String>) -> Self {
        Assignment { known, consumers: BTreeMap::new() }
    }

    /// Record that `consumer` uses observation `id`. An error if another consumer already
    /// uses it, or if it is neither a SATCOM ID in the table nor of the form `<source>:<item>`.
    pub fn claim(&mut self, id: &str, consumer: &str) -> Result<(), String> {
        let valid = match id.split_once(':') {
            Some((source, item)) => !source.is_empty() && !item.is_empty(),
            None => self.known.contains(id),
        };
        if !valid {
            return Err(format!(
                "{consumer}: unknown observation {id} (SATCOM IDs are <epoch>.bto, <epoch>.bfo or \
                 <epoch>.<event> from the observation table; other data are <source>:<item>)"
            ));
        }
        if let Some(other) = self.consumers.get(id) {
            return Err(format!("observation {id} is used twice: by {other} and by {consumer}"));
        }
        self.consumers.insert(id.to_string(), consumer.to_string());
        Ok(())
    }

    pub fn into_map(self) -> BTreeMap<String, String> {
        self.consumers
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn an_observation_used_twice_is_rejected() {
        let known: BTreeSet<String> = ["m0019a.bto", "m0019a.bfo", "m0019a.logon"].map(String::from).into();
        let mut assignment = Assignment::new(&known);
        assignment.claim("m0019a.bto", "cruise filter").unwrap();
        assignment.claim("m0019a.logon", "end-of-flight").unwrap();
        assignment.claim("debris:flaperon-reunion", "debris-drift").unwrap();

        let twice = assignment.claim("m0019a.bto", "terminal option r600").unwrap_err();
        assert!(twice.contains("cruise filter") && twice.contains("terminal option r600"), "{twice}");
        // A second module using the same find, under the same source prefix, collides too.
        assert!(assignment.claim("debris:flaperon-reunion", "another-module").is_err());
        // Unknown SATCOM IDs and IDs of neither form are refused rather than silently owned.
        assert!(assignment.claim("m0019c.bto", "terminal option").is_err());
        assert!(assignment.claim("flaperon", "debris-drift").is_err());
        assert!(assignment.claim(":item", "debris-drift").is_err());

        let map = assignment.into_map();
        assert_eq!(map.len(), 3);
        assert_eq!(map["m0019a.logon"], "end-of-flight");
    }
}
