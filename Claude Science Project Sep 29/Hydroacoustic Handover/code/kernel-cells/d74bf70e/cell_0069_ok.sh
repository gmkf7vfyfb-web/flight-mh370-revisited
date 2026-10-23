cd build
cat > at_src/at/BUILD-NOTES.txt <<EOF
Acoustics Toolbox (M. B. Porter, HLS Research), release at_2026_8_29.zip, GPL-3.0 (LICENSE).
Source: http://oalib.hlsresearch.com/AcousticsToolbox/at_2026_8_29.zip
sha256 307773ce2e0bc05a8131d8ec1d02a056bdd4d7545a1ae47fdedca2f8d28520d7, 40,439,628 bytes, fetched 2026-10-08.
Built 2026-10-08 on darwin arm64 with conda-forge gfortran from env mh370-hydro:
  make -k all FC=gfortran FFLAGS="-O2 -std=gnu -ffree-line-length-none -mcpu=native -I../misc -I../tslib" LAPACK_LIBS=-llapack
  in misc, tslib, Kraken, KrakenField, Bellhop (Scooter, Krakel not built).
Validation: kraken.exe on an ideal waveguide (vacuum surface, rigid bottom, c=1500 m/s, H=100 m, 50 Hz)
  reproduces all 7 analytic modes k_n = sqrt((w/c)^2 - ((n-1/2)pi/H)^2); max relative error
  1.34e-3 / 8.36e-5 / 5.23e-6 at 500 / 2000 / 8000 mesh points (second order in mesh spacing).
Run binaries with the mh370-hydro env active (dynamic libgfortran from that env).
EOF
tar czf acoustics-toolbox-build-arm64.tar.gz -C at_src/at LICENSE BUILD-NOTES.txt Kraken/kraken.exe Kraken/krakenc.exe Kraken/bounce.exe KrakenField/field.exe KrakenField/field3d.exe Bellhop/bellhop.exe Bellhop/bellhop3d.exe "Kraken/Kraken User Guide.pdf" build_misc.log build_tslib.log build_Kraken.log build_KrakenField.log build_Bellhop.log
ls -la acoustics-toolbox-build-arm64.tar.gz; otool -L at_src/at/Kraken/kraken.exe | head