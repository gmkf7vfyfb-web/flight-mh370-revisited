panel_letter(b, "b")
fig.savefig("hydro/sct/synthetic-composer-test.png", dpi=300, bbox_inches="tight")
fig.savefig("hydro/sct/synthetic-composer-test.pdf", bbox_inches="tight")
print([t.get_text() for t in fig.findobj(mpl.text.Text) if t.get_text() in ("a","b")])
