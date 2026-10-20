Attributes {
    lon {
        String units "degrees_east";
        String long_name "Longitude";
        Float32 actual_range 0.0, 358.125;
        String standard_name "longitude";
        String axis "X";
    }
    time {
        String long_name "Time";
        String delta_t "0000-00-01 00:00:00";
        String standard_name "time";
        String axis "T";
        String avg_period "0000-00-01 00:00:00";
        String units "hours since 1800-01-01 00:00:0.0";
        Float64 actual_range 1875888.0, 1884624.0;
        String coordinate_defines "start";
        UInt32 _ChunkSizes 1;
    }
    lat {
        String units "degrees_north";
        Float32 actual_range 88.542, -88.542;
        String long_name "Latitude";
        String standard_name "latitude";
        String axis "Y";
    }
    uwnd {
        String long_name "mean Daily u-wind at 10 m";
        String units "m/s";
        Int16 precision 2;
        Int16 least_significant_digit 1;
        Int16 GRIB_id 33;
        String GRIB_name "U GRD";
        String var_desc "u-wind";
        String dataset "NCEP Reanalysis Daily Averages";
        String level_desc "10 m";
        Float32 missing_value -9.96921E36;
        Float32 valid_range -102.2, 102.2;
        Float32 actual_range -23.725, 27.449997;
        String statistic "Mean";
        String parent_stat "Individual Obs";
        UInt32 _ChunkSizes 1, 94, 192;
    }
    time_bnds {
        UInt32 _ChunkSizes 1, 2;
    }
    NC_GLOBAL {
        String Conventions "COARDS";
        String title "mean daily NMC reanalysis (2014)";
        String history "created 2013/12 by Hoop (netCDF2.3)";
        String description "Data is from NMC initialized reanalysis
(4x/day).  It consists of T62 variables interpolated to
pressure surfaces from model (sigma) surfaces.";
        String platform "Model";
        String dataset_title "NCEP-NCAR Reanalysis 1";
        String References "http://www.psl.noaa.gov/data/gridded/data.ncep.reanalysis.html";
        String _NCProperties "version=2,netcdf=4.6.3,hdf5=1.10.5";
    }
    DODS_EXTRA {
        String Unlimited_Dimension "time";
    }
}
