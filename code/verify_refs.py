# -*- coding: utf-8 -*-
"""Check every DOI in the manuscript against Crossref before anything else.

Two traps this has hit before: records that are supplementary-material stubs
rather than the paper, and author fields returned in block capitals or with
initials folded into the family name. Both are reported rather than silently
accepted.
"""
import json, time, urllib.error, urllib.request

MAIL = "sandler.leon@gmail.com"
DOIS = [
    ("Abegglen 2015",   "10.1001/jama.2015.13134"),
    ("Cisneros 2017",   "10.1371/journal.pone.0176258"),
    ("Davies 2011",     "10.1088/1478-3975/8/1/015001"),
    ("Domazet-Loso 2010","10.1186/1741-7007-8-66"),
    ("Firsanov 2025",   "10.1038/s41586-025-09694-5"),
    ("Gatenby 2009",    "10.1158/0008-5472.CAN-08-3658"),
    ("Lineweaver 2014", "10.1002/bies.201400070"),
    ("Lineweaver 2021", "10.1002/bies.202000305"),
    ("Trigos 2017",     "10.1073/pnas.1617743114"),
]


def get(doi):
    url = "https://api.crossref.org/works/" + urllib.request.quote(doi)
    r = urllib.request.Request(url, headers={"User-Agent": "ref-check/1.0 (mailto:%s)" % MAIL})
    with urllib.request.urlopen(r, timeout=45) as resp:
        return json.load(resp)["message"]


out, bad = {}, []
for tag, doi in DOIS:
    try:
        m = get(doi)
    except urllib.error.HTTPError as e:
        print("%-18s %-34s NOT FOUND (%s)" % (tag, doi, e.code)); bad.append(tag); continue
    title = (m.get("title") or ["?"])[0]
    year = (m.get("issued", {}).get("date-parts") or [[None]])[0][0]
    jrnl = (m.get("container-title") or ["?"])[0]
    auth = m.get("author") or []
    names = ["%s %s" % (a.get("family", "?"), "".join(w[0] for w in (a.get("given") or "").split()))
             for a in auth]
    flags = []
    if m.get("type") not in ("journal-article", "posted-content"):
        flags.append("TYPE=" + str(m.get("type")))
    if any(a.get("family", "").isupper() for a in auth):
        flags.append("CAPS")
    if ".s0" in doi.lower():
        flags.append("SUPPLEMENTARY")
    out[tag] = {"doi": doi, "title": title, "year": year, "journal": jrnl,
                "authors": names, "volume": m.get("volume"), "page": m.get("page")}
    print("%-18s %s (%s) %s%s" % (tag, jrnl, year, title[:58],
                                  "  << " + ",".join(flags) if flags else ""))
    if flags:
        bad.append(tag)
    time.sleep(0.3)

json.dump(out, open("_refs_verified.json", "w"), indent=1)
print("\n%d/%d verified; flagged: %s" % (len(out), len(DOIS), bad or "none"))
