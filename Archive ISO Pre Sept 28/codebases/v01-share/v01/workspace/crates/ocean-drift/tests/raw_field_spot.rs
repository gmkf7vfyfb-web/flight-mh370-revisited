use std::{env, fs::File, io::BufReader};

use mh370_domain::LatLon;
use mh370_ocean_drift::GriddedField;

fn load_field(name: &str, environment_variable: &str) -> GriddedField {
    let path = env::var(environment_variable).unwrap();
    let file = File::open(path).unwrap();
    GriddedField::from_reader(name, BufReader::with_capacity(1024 * 1024, file)).unwrap()
}

#[test]
#[ignore = "requires converted external current, Stokes, and wind fields"]
fn converted_fields_match_independently_read_raw_netcdf_points() {
    let hycom = load_field("HYCOM", "MH370_HYCOM_FIELD");
    let hycom_sample = hycom
        .velocity(
            1_394_236_800.0,
            LatLon::new(-29.840_000_152_587_89, 95.439_941_406_25).unwrap(),
        )
        .unwrap();
    assert!((hycom_sample.east_mps - (-0.419)).abs() < 1e-6);
    assert!((hycom_sample.north_mps - (-0.191)).abs() < 1e-6);

    let gdp = load_field("GDP", "MH370_GDP_FIELD");
    let gdp_sample = gdp
        .velocity(1_394_236_800.0, LatLon::new(-29.875, 95.125).unwrap())
        .unwrap();
    assert!((gdp_sample.east_mps - 0.049_427_301_716_0).abs() < 1e-8);
    assert!((gdp_sample.north_mps - (-0.025_599_333_073_5)).abs() < 1e-8);
    assert!((gdp_sample.east_standard_error_mps - 0.021_302_482_238_2).abs() < 1e-8);
    assert!((gdp_sample.north_standard_error_mps - 0.021_509_139_966_8).abs() < 1e-8);

    let stokes = load_field("ERA5 Stokes", "MH370_STOKES_FIELD");
    let stokes_sample = stokes
        .velocity(1_394_236_800.0, LatLon::new(-30.0, 95.0).unwrap())
        .unwrap();
    assert!((stokes_sample.east_mps - (-0.042_269_557_714_462_28)).abs() < 1e-8);
    assert!((stokes_sample.north_mps - 0.097_852_222_621_440_89).abs() < 1e-8);

    let wind = load_field("NCEP R2 wind", "MH370_WIND_FIELD");
    let wind_sample = wind
        .velocity(
            1_388_534_400.0,
            LatLon::new(-12.380_649_566_650_39, 73.125).unwrap(),
        )
        .unwrap();
    // Independently interpolated between the enclosing T62 Gaussian rows
    // (-12.3808002472 and -10.4760398865 degrees) before MHGRID packing.
    assert!((wind_sample.east_mps - (-1.529_777_288_436_889_6)).abs() < 1e-7);
    assert!((wind_sample.north_mps - 0.139_865_696_430_206_3).abs() < 1e-7);
}

#[test]
#[ignore = "requires converted external wind field"]
fn regridded_wind_matches_independent_gaussian_row_interpolation() {
    let wind = load_field("NCEP R2 wind", "MH370_WIND_FIELD");
    let sample = wind
        .velocity(
            1_388_534_400.0,
            LatLon::new(-12.380_649_566_650_39, 73.125).unwrap(),
        )
        .unwrap();
    assert!((sample.east_mps - (-1.529_777_288_436_889_6)).abs() < 1e-7);
    assert!((sample.north_mps - 0.139_865_696_430_206_3).abs() < 1e-7);
}

#[test]
#[ignore = "requires extended native-resolution CMEMS current field"]
fn extended_glorys12_matches_raw_netcdf_node_with_packing_tolerance() {
    let currents = load_field("CMEMS GLORYS12", "MH370_GLORYS12_FIELD");
    let sample = currents
        .velocity(
            1_394_236_800.0,
            LatLon::new(-35.0, 64.166_664_123_535_16).unwrap(),
        )
        .unwrap();
    // Raw 2014-03-08 values are -0.22278511897 and -0.01770073548
    // m/s. The recorded MHGRID packing scale is exactly 0.001 m/s.
    assert!((sample.east_mps - (-0.223)).abs() < 1e-12);
    assert!((sample.north_mps - (-0.018)).abs() < 1e-12);
}

#[test]
#[ignore = "requires extended native-resolution CMEMS Stokes field"]
fn extended_waverys_matches_raw_netcdf_node_with_packing_tolerance() {
    let stokes = load_field("CMEMS WAVERYS", "MH370_WAVERYS_FIELD");
    let sample = stokes
        .velocity(1_394_236_800.0, LatLon::new(-35.0, 90.0).unwrap())
        .unwrap();
    // Raw 2014-03-08 00:00 values are exactly 0.04 and 0.09 m/s.
    assert!((sample.east_mps - 0.04).abs() < 1e-12);
    assert!((sample.north_mps - 0.09).abs() < 1e-12);
}
