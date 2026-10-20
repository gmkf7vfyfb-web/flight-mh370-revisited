Attributes {
    xu_ocean {
        String long_name "ucell longitude";
        String units "degrees_E";
        String cartesian_axis "X";
        Int32 domain_decomposition 1, 3600, 1, 1800;
        UInt32 _ChunkSizes 300;
    }
    yu_ocean {
        String long_name "ucell latitude";
        String units "degrees_N";
        String cartesian_axis "Y";
        Int32 domain_decomposition 1, 1500, 1, 150;
        UInt32 _ChunkSizes 300;
    }
    st_ocean {
        String long_name "tcell zstar depth";
        String units "meters";
        String cartesian_axis "Z";
        String positive "down";
        String edges "st_edges_ocean";
        UInt32 _ChunkSizes 51;
    }
    Time {
        String long_name "Time";
        String units "days since 1979-01-01 00:00:00";
        String cartesian_axis "T";
        String calendar_type "GREGORIAN";
        String calendar "GREGORIAN";
        String bounds "Time_bounds";
        UInt32 _ChunkSizes 1;
    }
    nv {
        UInt32 _ChunkSizes 2;
    }
    st_edges_ocean {
        String long_name "tcell zstar depth edges";
        String units "meters";
        String cartesian_axis "Z";
        String positive "down";
        UInt32 _ChunkSizes 52;
    }
    average_T1 {
        String long_name "Start time for average period";
        String units "days since 1979-01-01 00:00:00";
        Float64 missing_value 1.0E20;
        Float64 _FillValue 1.0E20;
        UInt32 _ChunkSizes 1;
    }
    average_T2 {
        String long_name "End time for average period";
        String units "days since 1979-01-01 00:00:00";
        Float64 missing_value 1.0E20;
        Float64 _FillValue 1.0E20;
        UInt32 _ChunkSizes 1;
    }
    average_DT {
        String long_name "Length of average period";
        String units "days";
        Float64 missing_value 1.0E20;
        Float64 _FillValue 1.0E20;
        UInt32 _ChunkSizes 1;
    }
    Time_bounds {
        String long_name "Time axis boundaries";
        String units "days";
        Float64 missing_value 1.0E20;
        Float64 _FillValue 1.0E20;
        UInt32 _ChunkSizes 1, 2;
    }
    u {
        String long_name "i-current";
        String units "m/sec";
        Int16 valid_range -32767, 32767;
        Int16 missing_value -32768;
        Int16 _FillValue -32768;
        Int32 packing 4;
        Float32 scale_factor 3.051851E-4;
        Float32 add_offset 0.0;
        String cell_methods "time: mean";
        String time_avg_info "average_T1,average_T2,average_DT";
        String coordinates "geolon_c geolat_c";
        String standard_name "sea_water_x_velocity";
        UInt32 _ChunkSizes 1, 1, 300, 300;
    }
    NC_GLOBAL {
        String filename "TMP/ocean_ofam_2014_03_01.nc.0000";
        Int32 NumFilesInSet 20;
        String title "BRAN_2016";
        String grid_type "regular";
        String grid_tile "N/A";
        String history "Wed Nov  2 11:33:06 2016: ncrcat -O ocean_u_2014_03_01.nc ocean_u_2014_03_02.nc ocean_u_2014_03_03.nc ocean_u_2014_03_04.nc ocean_u_2014_03_05.nc ocean_u_2014_03_06.nc ocean_u_2014_03_07.nc ocean_u_2014_03_08.nc ocean_u_2014_03_09.nc ocean_u_2014_03_10.nc ocean_u_2014_03_11.nc ocean_u_2014_03_12.nc ocean_u_2014_03_13.nc ocean_u_2014_03_14.nc ocean_u_2014_03_15.nc ocean_u_2014_03_16.nc ocean_u_2014_03_17.nc ocean_u_2014_03_18.nc ocean_u_2014_03_19.nc ocean_u_2014_03_20.nc ocean_u_2014_03_21.nc ocean_u_2014_03_22.nc ocean_u_2014_03_23.nc ocean_u_2014_03_24.nc ocean_u_2014_03_25.nc ocean_u_2014_03_26.nc ocean_u_2014_03_27.nc ocean_u_2014_03_28.nc ocean_u_2014_03_29.nc ocean_u_2014_03_30.nc ocean_u_2014_03_31.nc /g/data1/p93/raf599/BRAN_2016/OFAM/ocean_u_2014_03.nc";
        String NCO "\"4.5.3\"";
        Int32 nco_openmp_thread_number 1;
    }
    DODS_EXTRA {
        String Unlimited_Dimension "Time";
    }
}
