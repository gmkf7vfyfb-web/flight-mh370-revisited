Attributes {
    lon {
        String long_name "longitude";
        String standard_name "longitude";
        String units "degrees_east";
        String axis "X";
        Float64 valid_min 0.;
        Float64 valid_max 359.75;
        String bounds "[0,359.75]";
    }
    time {
        String long_name "time centered on the day";
        String standard_name "time";
        String units "days since 1990-1-1";
        String calendar "julian";
        String axis "T";
        String time_bounds "2014-03-08 00:00:00 to 2014-03-08 23:59:59";
        String comment "Data is averaged over the day";
    }
    lat {
        String long_name "latitude";
        String standard_name "latitude";
        String units "degrees_north";
        String axis "Y";
        Float64 valid_min -89.75;
        Float64 valid_max 89.75;
        String bounds "[-89.75,89.75]";
    }
    u {
        Float64 _FillValue -999.;
        String long_name "zonal total surface current";
        String standard_name "eastward_sea_water_velocity";
        String units "m s-1";
        String coverage_content_type "modelResult";
        Float64 valid_min -3.;
        Float64 valid_max 3.;
        String coordinates "lon lat";
        String depth "15m";
        String comment "Velocities are an average over the top 30m of the mixed layer";
        String source "SSH source: CMEMS SSALTO/DUACS SEALEVEL_GLO_PHY_L4_MY_008_047 DOI: 10.48670/moi-00148 ; WIND source: ECMWF ERA5 10m wind DOI: 10.24381/cds.adbb2d47 ; SST source: CMC 0.2 deg SST V2.0 DOI: 10.5067/GHCMC-4FM02";
    }
    vg {
        Float64 _FillValue -999.;
        String long_name "meridional geostrophic surface current";
        String standard_name "geostrophic_northward_sea_water_velocity";
        String units "m s-1";
        Float64 valid_min -3.;
        Float64 valid_max 3.;
        String coordinates "lon lat";
        String depth "15m";
        String comment "Geostrophic velocities calculated from absolute dynamic topography";
        String source "SSH source: CMEMS SSALTO/DUACS SEALEVEL_GLO_PHY_L4_MY_008_047 DOI: 10.48670/moi-00148";
    }
    ug {
        Float64 _FillValue -999.;
        String long_name "zonal geostrophic surface current";
        String standard_name "geostrophic_eastward_sea_water_velocity";
        String units "m s-1";
        Float64 valid_min -3.;
        Float64 valid_max 3.;
        String coordinates "lon lat";
        String depth "15m";
        String comment "Geostrophic velocities calculated from absolute dynamic topography";
        String source "SSH source: CMEMS SSALTO/DUACS SEALEVEL_GLO_PHY_L4_MY_008_047 DOI: 10.48670/moi-00148";
    }
    v {
        Float64 _FillValue -999.;
        String long_name "meridional total surface current";
        String standard_name "northward_sea_water_velocity";
        String units "m s-1";
        String coverage_content_type "modelResult";
        Float64 valid_min -3.;
        Float64 valid_max 3.;
        String coordinates "lon lat";
        String depth "15m";
        String comment "Velocities are an average over the top 30m of the mixed layer";
        String source "SSH source: CMEMS SSALTO/DUACS SEALEVEL_GLO_PHY_L4_MY_008_047 DOI: 10.48670/moi-00148 ; WIND source: ECMWF ERA5 10m wind DOI: 10.24381/cds.adbb2d47 ; SST source: CMC 0.2 deg SST V2.0 DOI: 10.5067/GHCMC-4FM02";
    }
    build_dmrpp_metadata {
        String created "2026-08-19T04:25:34Z";
        String build_dmrpp "3.21.1-1090";
        String bes "3.21.1-1090";
        String libdap "libdap-3.21.1-389";
        String invocation "build_dmrpp -f /tmp/tmp7wojkoie/oscar_currents_final_20140308.nc -r oscar_currents_final_20140308.nc.dmr -u OPeNDAP_DMRpp_DATA_ACCESS_URL -M";
    }
    DAP4_GLOBAL {
        String title "Ocean Surface Current Analyses Real-time (OSCAR) Surface Currents - Final 0.25 Degree (Version 2.0)";
        String summary "Global, daily, 0.25 degree geostrophic and total mixed layer currents averaged over the top 30m. Highest quality OSCAR product.";
        String keywords "ocean currents,ocean circulation,surface currents,ekman,geostrophic";
        String Conventions "CF-1.8 Standard Names v77, ACDD-1.3, netcdf 4.7.3, hdf5 1.8.12";
        String id "OSCAR_L4_OC_FINAL_V2.0";
        String history "OSCAR 0.25 degree daily version 2.0 replaces OSCAR third degree 5 day";
        String source "OSCAR is based on simplified physics using satellite data; SSH source: CMEMS SSALTO/DUACS SEALEVEL_GLO_PHY_L4_MY_008_047 DOI: 10.48670/moi-00148 ; WIND source: ECMWF ERA5 10m wind DOI: 10.24381/cds.adbb2d47 ; SST source: CMC 0.2 deg SST V2.0 DOI: 10.5067/GHCMC-4FM02";
        String processing_level "L4";
        String standard_name_vocabulary "NetCDF Climate and Forecast (CF) Metadata Convention";
        String acknowledgment "OSCAR products are supported by NASA and may be freely distributed.";
        String product_version "v2.0";
        String creator_name "Kathleen Dohan";
        String creator_email "kdohan@esr.org";
        String creator_url "www.esr.org/research/oscar/";
        String creator_type "person";
        String creator_institution "ESR";
        String institution "Earth & Space Research";
        String references "www.esr.org/research/oscar/, PO.DAAC user guide, DOI: 10.5067/OSCAR-25F20";
        String project "Ocean Surface Current Analyses Real-time (OSCAR)";
        String program "OSCAR";
        String publisher_name "NASA Physical Oceanography Distributed Active Archive Center (PO.DAAC)";
        String publisher_email "podaac@podaac.jpl.nasa.gov";
        String publisher_url "podaac.jpl.nasa.gov";
        String publisher_type "institution";
        String publisher_institution "PO.DAAC";
        Float64 geospatial_lat_min -89.75;
        Float64 geospatial_lat_max 89.75;
        String geospatial_lat_units "degrees_north";
        String geospatial_lat_resolution "0.25 degree";
        Float64 geospatial_lon_min 0.;
        Float64 geospatial_lon_max 359.75;
        String geospatial_lon_units "degrees_east";
        String geospatial_lon_resolution "0.25 degree";
        String time_coverage_start "2014-03-08T00:00:00";
        String time_coverage_end "2014-03-08T23:59:59";
        String date_created "2022-01-09";
    }
}
