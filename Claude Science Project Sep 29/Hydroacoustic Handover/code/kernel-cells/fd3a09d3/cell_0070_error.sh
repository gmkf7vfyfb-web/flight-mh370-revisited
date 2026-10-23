cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import pathlib
p=pathlib.Path('tl_grid_charts.py'); s=p.read_text()
old='''def footnotes(fig, plain, tech, y0=0.005):
    fig.text(0.01, y0 + 0.052, textwrap.fill("Plain-language note: " + plain, 230), fontsize=6, va="bottom", color="#333333")
    fig.text(0.01, y0, textwrap.fill("Technical note: " + tech, 230), fontsize=6, va="bottom", color="#333333")'''
new='''def footnotes(fig, plain, tech, y0=0.005):
    t = textwrap.fill("Technical note: " + tech, 235); n = t.count("\\n") + 1
    fig.text(0.01, y0, t, fontsize=6, va="bottom", color="#333333", linespacing=1.25)
    fig.text(0.01, y0 + 0.0115 * n + 0.012, textwrap.fill("Plain-language note: " + plain, 235), fontsize=6, va="bottom", color="#333333", linespacing=1.25)


def ridge_shade(ax, ims):
    r = ims[(ims.offset_nm == 0) & ims.ridge_source].lat.unique()
    for la in r:
        ax.axvspan(-la - 0.25, -la + 0.25, color="#fbe3c8", zorder=0, lw=0)'''
assert old in s; s=s.replace(old,new,1)
s=s.replace('''    fig, axes = plt.subplots(2, 4, figsize=(13, 7.6), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.05, right=0.99, top=0.86, bottom=0.2, wspace=0.08, hspace=0.3)
    for ax, rec in zip(axes.ravel(), ORDER):
        g = d[d.receiver == rec]
        for fc in SHOW_BANDS:''','''    fig, axes = plt.subplots(2, 4, figsize=(13, 8.2), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.05, right=0.99, top=0.87, bottom=0.24, wspace=0.08, hspace=0.3)
    for ax, rec in zip(axes.ravel(), ORDER):
        g = d[d.receiver == rec]; ridge_shade(ax, ims)
        for fc in SHOW_BANDS:''')
s=s.replace('''        if rec == "H01W":
            ax.text(41.2, 263.5, "x = band blocked (no sound reaches the receiver)", fontsize=6, va="top", color="#444444")''',
'''        if rec == "H01W":
            ax.text(41.2, 263.5, "x = band blocked (no sound reaches the receiver)", fontsize=6, va="top", color="#444444")
            ax.text(41.2, 104, "orange band = source over Broken Ridge (< 2,000 m water)", fontsize=6, va="bottom", color="#8a5a1e")''')
s=s.replace('''    fig.suptitle("Sound transmission loss from the 7th arc to each receiver: lower loss for Cape Leeuwin and Perth Canyon, blocked paths to Diego Garcia North and much of Scott Reef",
                 x=0.01, ha="left", fontsize=9)''',
'''    fig.suptitle("Sound transmission loss from the 7th arc to each receiver, by source latitude: Diego Garcia North is blocked from almost everywhere, Scott Reef from south of 29.5°S",
                 x=0.01, ha="left", fontsize=9)''')
s=s.replace('''              "sends no sound through. The thin lines are for sources 30 nautical miles (56 km) west and east of the arc. Values are estimates from a model of "
              "the ocean; they are not measurements, and the model is not yet calibrated.",''',
'''              "sends no sound through. The thin lines are for sources 30 nautical miles (56 km) west and east of the arc. In the orange band the source sits over "
              "Broken Ridge in water less than 2,000 m deep; the model then lets more sound into the deep channel, and this part of the model is not validated. "
              "Values are estimates from a model of the ocean; they are not measurements, and the model is not yet calibrated.",''')
s=s.replace('''"(or land on track, or zero field at the receiver). Arc = zero contour''','''"(or land on track, or zero field at the receiver); at Portland the 5 Hz line is the RAM reference value that rule 2 assigns to a no-mode band. ridge_source rows (orange) "
              "are flagged (reach gap G-N2/K5); at Portland their RAM-corrected value is floored at the reference RAM value (tl_grid_table.py). Arc = zero contour''')
s=s.replace('''    fig, axes = plt.subplots(2, 4, figsize=(13, 7.6), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.05, right=0.99, top=0.86, bottom=0.2, wspace=0.08, hspace=0.3)
    for ax, rec in zip(axes.ravel(), ORDER):
        g = d[d.receiver == rec]
        for eta in''','''    ims = pd.read_csv(pathlib.Path(a_table) / "ims_tl_kraken_arc.csv")
    fig, axes = plt.subplots(2, 4, figsize=(13, 8.2), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.05, right=0.99, top=0.87, bottom=0.24, wspace=0.08, hspace=0.3)
    for ax, rec in zip(axes.ravel(), ORDER):
        g = d[d.receiver == rec]; ridge_shade(ax, ims)
        for eta in''')
s=s.replace('def chart_detect(ev_dir, out, stamp):','def chart_detect(ev_dir, out, stamp, a_table):')
s=s.replace('chart_detect(pathlib.Path(a.ev_dir), out, a.stamp)','chart_detect(pathlib.Path(a.ev_dir), out, a.stamp, a.table_dir)')
s=s.replace('''    fig.suptitle("Share of simulated impacts that would be detectable at each receiver: only with a high coupling efficiency, and mainly south of 30°S for Cape Leeuwin",
                 x=0.01, ha="left", fontsize=9)''','''    fig.suptitle("Share of simulated impacts that would be detectable at each receiver: appreciable only for a coupling efficiency of 0.001 or more, and smaller north of 30°S",
                 x=0.01, ha="left", fontsize=9)''')
s=s.replace('''"receiver, for four assumed values of the share of impact energy that becomes sound. The impact energies come from the project's end-of-flight "
              "simulation (run J). The dashed line uses a stricter rule: the sound must be above the loudest 5-10 % of the background noise. These are model "
              "predictions, not detections; the sound-loss model is not yet calibrated.",''','''"receiver, for four assumed values of the share of impact energy that becomes sound. The impact energies come from the project's end-of-flight "
              "simulation (run J). The dashed line uses a stricter rule: the sound must be above the loudest 5-10 % of the background noise. In the orange band the "
              "source sits over Broken Ridge (water less than 2,000 m deep), where the model is not validated. These are model predictions, not detections; the "
              "sound-loss model is not yet calibrated.",''')
p.write_text(s)
EOF
python -c "import ast; ast.parse(open('tl_grid_charts.py').read()); print('ok')"
export PYTHONPATH=.; python tl_grid_evidence.py /tmp/tlg_tables_A /tmp/tlg_ev_A > /dev/null && python tl_grid_charts.py /tmp/tlg_tables_A /tmp/tlg_ev_A /tmp/tlg_charts_A --stamp "pass A only (offset 0), draft" && cp /tmp/tlg_charts_A/*.png drafts/