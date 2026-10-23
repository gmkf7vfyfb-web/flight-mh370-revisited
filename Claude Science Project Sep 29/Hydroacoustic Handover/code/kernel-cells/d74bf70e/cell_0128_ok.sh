curl -s -m 60 "https://dap.ceda.ac.uk/thredds/catalog/bodc/gebco/global/catalog.html" | grep -o -E "href='[^']*'|href=\"[^\"]*\"" | grep -i gebco | head -15
echo ===WOA
curl -s -m 60 "https://www.ncei.noaa.gov/thredds-ocean/catalog/woa23/DATA/temperature/netcdf/catalog.html" | grep -o -E "href='[^']*'|href=\"[^\"]*\"" | head -20