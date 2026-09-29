"""Independent reference calculation; no import from the product fuel code.

Run: python3 fuel_reference_check.py [project-directory]
Reference inputs are official calculated outputs, not measured fuel histories.
All model coefficients/settings are read from frozen declared inputs; none fit.
"""
import hashlib
import json
import math
from pathlib import Path
import sys

directory = Path(__file__).resolve().parent
project = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/jackbox/home/MH370')
profile_path = project / '.sources/ulich-mh370-fuel-performance/data/official_post_acars.json'
rows_path = project / '.sources/martin-bsm-trent892-lrc/data/coefficient-pins.json'
condition_path = directory / 'fuel-condition.json'
endurance_path = directory / 'fuel-endurance-reference-inputs.json'
profile = json.loads(profile_path.read_text())
rows = json.loads(rows_path.read_text())['rows']
condition = json.loads(condition_path.read_text())
reference = json.loads(endurance_path.read_text())
extension = condition['model']
zfw = condition['zero_fuel_weight_kg']
identities = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in [Path(__file__), profile_path, rows_path, condition_path, endurance_path]}


def coefficients(flight_level, mach, common_scale=1.0):
    level = min(410.0, max(350.0, flight_level))
    upper = next(i for i, row in enumerate(rows) if row['flight_level'] >= level)
    lower = max(0, upper-1)
    first, last = rows[lower], rows[upper]
    fraction = 0.0 if lower == upper else (level-first['flight_level'])/(last['flight_level']-first['flight_level'])
    a, b = [first[k]*(1-fraction)+last[k]*fraction
            for k in ['intercept_kg_s', 'gross_mass_coefficient_s_inv']]
    scale = math.exp(math.log(common_scale*extension['nominal_flow_scale'])
                     + extension['mach_log_sensitivity_per_mach']*(mach-extension['reference_mach'])
                     + extension['below_fl350_log_sensitivity_per_1000_ft']*max(0,350-flight_level)/10
                     + extension['above_fl410_log_sensitivity_per_1000_ft']*max(0,flight_level-410)/10)
    scale = min(extension['maximum_flow_multiplier'], max(extension['minimum_flow_multiplier'], scale))
    return a*scale, b*scale, scale


mass = zfw+profile['initial_fuel_kg']
segments = []
for row in profile['segments']:
    a,b,scale = coefficients(row['flight_level'],row['mach'])
    end = (mass+a/b)*math.exp(-b*row['duration_h']*3600)-a/b
    segments.append(dict(segment=row['segment'], model_burn_kg=mass-end,
                         model_ending_fuel_kg=end-zfw,
                         official_calculated_ending_fuel_kg=row['official_ending_fuel_lb']*0.45359237,
                         declared_flow_multiplier=scale))
    mass = end
path = directory/'fuel-reference-profile-assessment.json'
assessment = {
    'model': 'DeclaredBroadExtension of the supplied Martin/BSM LRC rows',
    'classification': 'comparison with official calculated outputs, not measured cruise validation',
    'source_url': reference['source_url'],
    'located_passages': 'Official Appendix 1.6E PDF page 3 assumptions and page 5 Table 3',
    'initial_fuel_kg': profile['initial_fuel_kg'],
    'zero_fuel_mass_kg': zfw,
    'limitations': [
        'Printed constant-state segments total 4878s, 4.9s shorter than the stated Arc-1 epoch.',
        'Zero bank/vertical speed in each printed segment; scale1; no parameters fitted.',
        'Official references use Boeing/Rolls-Royce analyses with assumed altitude/speed histories.',
        'The separate 4226.524kg overburn belongs to the Ulich clean-room drag/ICAO proxy, not this model.',
        'One reference profile cannot calibrate the operating envelope or declared uncertainty intervals.',
    ],
}
assessment.update(segments=segments, predicted_total_burn_kg=profile['initial_fuel_kg']-(mass-zfw),
                  official_calculated_total_burn_kg=profile['initial_fuel_kg']-profile['official_arc1_ending_fuel_lb']*0.45359237,
                  ending_fuel_difference_kg=mass-zfw-profile['official_arc1_ending_fuel_lb']*0.45359237,
                  input_sha256=identities)
path.write_text(json.dumps(assessment,indent=2)+'\n')

m0 = zfw+profile['official_arc1_ending_fuel_lb']*0.45359237
mf = zfw+condition['inaccessible_fuel_kg']
records = []
for row in reference['records']:
    def endurance(scale):
        a,b,_ = coefficients(row['flight_level'],row['printed_mach'],scale)
        return math.log((a+b*m0)/(a+b*mf))/b/3600
    value = endurance(1.0)
    records.append(dict(row, current_model_endurance_h=value,
                        relative_endurance_difference=value/row['official_calculated_endurance_h']-1,
                        inside_current_nominal_cruise_bounds=250<=row['flight_level']<=430 and .73<=row['printed_mach']<=.84,
                        flow_scale_09_to_11_endurance_h=[endurance(1.1),endurance(.9)]))
path = directory/'fuel-endurance-reference-assessment.json'
assessment = {
    'source_url': reference['source_url'],
    'locator': reference['locator'],
    'source_classification': reference['classification'],
    'model_conditions': dict(initial_fuel_kg=m0-zfw, zero_fuel_mass_kg=zfw,
                             final_unusable_fuel_kg=mf-zfw, bank_deg=0,
                             vertical_speed_ft_min=0, nominal_flow_scale=1),
    'limitations': [
        'Both printed FL350/M0.824 cases are retained despite different TAS/endurance; no typo corrected.',
        'LRC rows describe variable-Mach LRC; the fixed reference-Mach extension is an approximation.',
        'This is a frozen diagnostic comparison, not a fit or validation against measurements.',
        'The stochastic cruise benchmark lacks full thrust, stall/buffet and VMO constraints.',
    ],
}
assessment.update(records=records,input_sha256=identities)
path.write_text(json.dumps(assessment,indent=2)+'\n')
print('Frozen fuel reference calculations regenerated; no parameters fitted.')
