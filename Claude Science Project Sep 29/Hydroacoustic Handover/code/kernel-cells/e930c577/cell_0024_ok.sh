cd ~/Downloads/mh370-ocean-data/gebco; ls -la . grid; cat grid/*.json | head -30; ls grid/*.json; python -c "
import netCDF4" 2>&1; python -c "import xarray, h5py; print('ok')" 2>&1; ls woa23 | head