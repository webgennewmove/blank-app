import html, pathlib
root = pathlib.Path(__file__).parent
tpl = (root / "page.template.html").read_text()
for n in "ABCDE":
    src = (root.parent / "diagrams" / f"{n}.mmd").read_text().rstrip("\n")
    esc = html.escape(src, quote=False)
    tpl = tpl.replace(f"@@MERMAID_{n}@@", esc).replace(f"@@SRC_{n}@@", esc)
assert "@@" not in tpl, "unreplaced placeholder"
out = root.parent / "magalo-citizen-brain.html"
out.write_text(tpl)
print(out, len(tpl), "bytes")
