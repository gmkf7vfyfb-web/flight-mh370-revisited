"""Coast regions used for the debris-fate tables and maps (17 Oct 2026). (name, lon_min, lon_max, lat_min, lat_max); first match wins."""
REGIONS = [
    ('Reunion, Mauritius, Rodrigues', 54.0, 64.5, -22.5, -19.0), ('Madagascar', 42.8, 51.0, -26.5, -11.8), ('Mozambique', 30.0, 41.2, -27.0, -10.4),
    ('South Africa', 15.0, 33.0, -36.0, -26.8), ('Tanzania, Kenya, Somalia', 38.0, 52.0, -10.4, 12.5), ('other western Indian Ocean islands', 42.0, 75.0, -15.0, 10.0),
    ('Western Australia', 111.0, 129.0, -36.5, -13.0), ('southern Australia (SA, Vic, Tas)', 129.0, 151.0, -45.0, -31.0), ('Indonesia, Timor, northern Australia', 94.0, 145.0, -16.0, 6.5),
    ('Sri Lanka, India, Bay of Bengal', 72.0, 100.0, 5.0, 25.0), ('southern islands (Amsterdam, Kerguelen, Crozet)', 35.0, 80.0, -50.0, -36.0)]
def region_of(lo, la):
    for nm, a, b_, c_, d in REGIONS:
        if a <= lo <= b_ and c_ <= la <= d: return nm
    return 'other coasts'
