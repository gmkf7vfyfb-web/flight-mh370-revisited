mkdir -p build && cd build
curl -s -m 600 -o at_2026_8_29.zip http://oalib.hlsresearch.com/AcousticsToolbox/at_2026_8_29.zip; ls -la at_2026_8_29.zip; shasum -a 256 at_2026_8_29.zip
unzip -q -o at_2026_8_29.zip -d at_src; ls at_src; ls at_src/* | head -30; du -sh at_src