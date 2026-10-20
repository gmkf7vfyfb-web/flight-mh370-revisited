//! The engine's own SATCOM measurement model, as a stand-alone oracle for analysis scripts.
//!
//!   cargo run --release --example predict -- epochs <observations.csv> <ephemeris.csv>
//!       one line per epoch: id, unix_s, satellite position and velocity (km, km/s), AFC term,
//!       BTO and its sd, BFO and its sd, cruise flags
//!   cargo run --release --example predict -- states <observations.csv> <ephemeris.csv> < states.csv
//!       states.csv rows: epoch_id,lat_deg,lon_deg,alt_ft,v_north_kt,v_east_kt,v_up_fpm
//!       output rows: the same plus predicted BTO (us) and predicted BFO without bias (Hz)
//!
//! It calls satcom::bto_us and satcom::bfo_without_bias_hz, so a script validated against it
//! uses the filter's measurement model rather than a re-derivation.
use std::io::{BufRead, Write};

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let epochs = satcom::load_epochs(a[2].as_ref(), a[3].as_ref()).expect("epochs");
    let out = std::io::stdout();
    let mut out = out.lock();
    let opt = |v: Option<f64>| v.map_or("".to_string(), |x| format!("{x:.6}"));
    match a[1].as_str() {
        "epochs" => {
            writeln!(out, "id,unix_s,sx,sy,sz,svx,svy,svz,afc_hz,bto_us,bto_sd_us,bfo_hz,bfo_sd_hz,cruise_bto,cruise_bfo").unwrap();
            for e in &epochs {
                let (p, v) = (e.satellite_km, e.satellite_velocity_km_s);
                writeln!(out, "{},{:.3},{:.9},{:.9},{:.9},{:.12},{:.12},{:.12},{:.9},{},{},{},{},{},{}", e.id, e.unix_s, p.x, p.y, p.z, v.x, v.y, v.z,
                    e.satellite_afc_hz, opt(e.bto_us), e.bto_sd_us, opt(e.bfo_hz), e.bfo_sd_hz, e.cruise_bto, e.cruise_bfo).unwrap();
            }
        }
        "states" => {
            for line in std::io::stdin().lock().lines() {
                let line = line.unwrap();
                let f: Vec<&str> = line.split(',').collect();
                let Some(e) = epochs.iter().find(|e| e.id == f[0]) else { continue };
                let x: Vec<f64> = f[1..7].iter().map(|s| s.parse().unwrap()).collect();
                let bto = satcom::bto_us(e.satellite_km, x[0], x[1], x[2]);
                let bfo = satcom::bfo_without_bias_hz(e, x[0], x[1], x[2], x[3], x[4], x[5]);
                writeln!(out, "{line},{bto:.9},{bfo:.9}").unwrap();
            }
        }
        m => panic!("unknown mode {m}"),
    }
}
