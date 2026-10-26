import html, pathlib
root = pathlib.Path(__file__).parent
head = """<title>MAGALO Police Brain</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="Design blueprint for MAGALO's AI police: dispatch, perception, pursuit, coordinated search, escalation, arrest, apartment safety, multiplayer cases and a vehicle roadmap.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&family=JetBrains+Mono:wght@400;600&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap">
"""
css = (root/"base.css").read_text() + (root/"police.css").read_text()
body = (root/"body.html").read_text()
for n in "ABCDEFG":
    src = (root.parent/"diagrams"/f"{n}.mmd").read_text().rstrip("\n")
    esc = html.escape(src, quote=False)
    body = body.replace(f"@@MERMAID_{n}@@", esc).replace(f"@@SRC_{n}@@", esc)
assert "@@" not in body, "unreplaced placeholder"
out = root.parent / "magalo-police-brain.html"
out.write_text(head + "<style>" + css + "</style>\n\n" + body)
print(out, len(out.read_text()), "bytes")
