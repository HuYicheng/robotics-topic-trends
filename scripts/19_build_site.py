"""Build the page from site_src/page.html.

site/index.html          full HTML document for GitHub Pages (doctype, head, body), with site/data.json beside it
site_preview/index.html  the same content without the document skeleton (the private claude.ai preview adds its own)
"""
import os
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
src = open(os.path.join(ROOT, "site_src", "page.html")).read()
head_end = src.index("</style>") + len("</style>")
head, body = src[:head_end], src[head_end:]
full = ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
        "<meta name=\"description\" content=\"Shares and trends of robotics research topics at ICRA, IROS, RSS, CoRL, T-RO, IJRR and Science Robotics, 2024-2026, with a topic-combination paper finder.\">\n"
        + head + "\n</head>\n<body>\n" + body + "\n</body>\n</html>\n")
os.makedirs(os.path.join(ROOT, "site"), exist_ok=True)
open(os.path.join(ROOT, "site", "index.html"), "w").write(full)
open(os.path.join(ROOT, "site", ".nojekyll"), "w").write("")
os.makedirs(os.path.join(ROOT, "site_preview"), exist_ok=True)
open(os.path.join(ROOT, "site_preview", "index.html"), "w").write(src)
shutil.copy(os.path.join(ROOT, "site", "data.json"), os.path.join(ROOT, "site_preview", "data.json"))
print("site/index.html", len(full), "bytes; site_preview/index.html", len(src), "bytes")
