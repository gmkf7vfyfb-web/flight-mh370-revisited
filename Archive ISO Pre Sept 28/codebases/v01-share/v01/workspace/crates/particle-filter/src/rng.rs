use rand::SeedableRng;
use rand_chacha::ChaCha8Rng;
use sha2::{Digest, Sha256};

pub fn derive_seed(
    master_seed: u64,
    purpose: &str,
    epoch: usize,
    particle: usize,
    substream: u64,
) -> [u8; 32] {
    let mut digest = Sha256::new();
    digest.update(b"mh370-smc-seed-v1\0");
    digest.update(master_seed.to_be_bytes());
    digest.update((purpose.len() as u64).to_be_bytes());
    digest.update(purpose.as_bytes());
    digest.update((epoch as u64).to_be_bytes());
    digest.update((particle as u64).to_be_bytes());
    digest.update(substream.to_be_bytes());
    digest.finalize().into()
}

pub fn rng_for(
    master_seed: u64,
    purpose: &str,
    epoch: usize,
    particle: usize,
    substream: u64,
) -> ChaCha8Rng {
    ChaCha8Rng::from_seed(derive_seed(
        master_seed,
        purpose,
        epoch,
        particle,
        substream,
    ))
}

/// Build a deterministic stream from an explicit, length-delimited coordinate
/// tuple. This is reserved for algorithms whose random identity cannot safely
/// depend on a population slot (for example, a fixed replicate within a stable
/// root lineage).
pub(crate) fn rng_for_coordinates(
    master_seed: u64,
    purpose: &str,
    epoch: usize,
    coordinates: &[u64],
) -> ChaCha8Rng {
    let mut digest = Sha256::new();
    digest.update(b"mh370-smc-coordinate-seed-v1\0");
    digest.update(master_seed.to_be_bytes());
    digest.update((purpose.len() as u64).to_be_bytes());
    digest.update(purpose.as_bytes());
    digest.update((epoch as u64).to_be_bytes());
    digest.update((coordinates.len() as u64).to_be_bytes());
    for coordinate in coordinates {
        digest.update(coordinate.to_be_bytes());
    }
    ChaCha8Rng::from_seed(digest.finalize().into())
}

#[cfg(test)]
mod tests {
    use rand::RngCore;

    use super::*;

    #[test]
    fn keyed_streams_are_repeatable_and_separated() {
        let mut first = rng_for(91, "propagate", 2, 7, 0);
        let mut second = rng_for(91, "propagate", 2, 7, 0);
        let mut other = rng_for(91, "propagate", 2, 8, 0);
        assert_eq!(first.next_u64(), second.next_u64());
        assert_ne!(first.next_u64(), other.next_u64());
    }

    #[test]
    fn coordinate_streams_are_repeatable_and_length_delimited() {
        let mut first = rng_for_coordinates(91, "root-candidate", 2, &[7, 11, 3]);
        let mut same = rng_for_coordinates(91, "root-candidate", 2, &[7, 11, 3]);
        let mut regrouped = rng_for_coordinates(91, "root-candidate", 2, &[7, 11, 3, 0]);
        let mut reordered = rng_for_coordinates(91, "root-candidate", 2, &[7, 3, 11]);
        assert_eq!(first.next_u64(), same.next_u64());
        assert_ne!(first.next_u64(), regrouped.next_u64());
        assert_ne!(same.next_u64(), reordered.next_u64());
    }
}
