use mh370_ocean_drift::{FLAPERON_RECOVERY_UNIX_S, MH370_SEVENTH_ARC_UNIX_S};

#[test]
fn canonical_utc_epochs_match_independent_unix_conversion() {
    // `date -u -d '2014-03-08 00:19:00' +%s`
    assert_eq!(MH370_SEVENTH_ARC_UNIX_S, 1_394_237_940.0);
    // `date -u -d '2015-07-29 00:00:00' +%s`
    assert_eq!(FLAPERON_RECOVERY_UNIX_S, 1_438_128_000.0);
}
