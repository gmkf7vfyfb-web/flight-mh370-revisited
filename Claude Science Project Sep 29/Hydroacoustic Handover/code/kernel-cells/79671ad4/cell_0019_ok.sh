cd src
B="https://www.ncei.noaa.gov/thredds-ocean/dodsC/woa23/DATA"
# lat index: -89.5 + i ; -25.5 -> 64, -26.5 -> 63. lon -179.5 + j ; 101.5 -> 281
for v in t s; do
 if [ $v = t ]; then P=temperature; D=decav; else P=salinity; D=decav; fi
 curl -sS -m 60 -o woa23_${v}03.asc "$B/$P/netcdf/$D/1.00/woa23_${D}_${v}03_01.nc.ascii?${v}_an%5B0%5D%5B0:56%5D%5B63:64%5D%5B281%5D,depth" -w "$v03 %{http_code}\n"
 curl -sS -m 60 -o woa23_${v}13.asc "$B/$P/netcdf/$D/1.00/woa23_${D}_${v}13_01.nc.ascii?${v}_an%5B0%5D%5B0:101%5D%5B63:64%5D%5B281%5D,depth" -w "$v13 %{http_code}\n"
done
ls -la; head -c 600 woa23_t03.asc