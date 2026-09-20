# -*- coding: utf-8 -*-
"""Find DOIs for the references the revision adds, by bibliographic search
rather than by guessing DOI strings. Each hit is printed with its title so a
wrong match is visible rather than silently adopted.
"""
import json, time, urllib.parse, urllib.request

MAIL = "sandler.leon@gmail.com"
QUERIES = {
 "seluanov2018":  "Mechanisms of cancer resistance in long-lived mammals Seluanov Gladyshev Vijg Gorbunova",
 "caulin2011":    "Peto's Paradox evolution's prescription for cancer prevention Caulin Maley",
 "lopezotin2023": "Hallmarks of aging an expanding universe Lopez-Otin Blasco Partridge Serrano Kroemer",
 "ferrell2002":   "Self-perpetuating states in signal transduction positive feedback double-negative feedback bistability Ferrell",
 "ceccaldi2016":  "Repair Pathway Choices and Consequences at the Double-Strand Break Ceccaldi Rondinelli D'Andrea",
 "vijg2020":      "Pathogenic mechanisms of somatic mutation and genome mosaicism in aging Vijg Dong",
 "scheffer2009":  "Early-warning signals for critical transitions Scheffer Bascompte Brock",
 "vandeursen2014":"The role of senescent cells in ageing van Deursen",
 "tian2013":      "High-molecular-mass hyaluronan mediates the cancer resistance of the naked mole rat Tian Azpurua Gorbunova",
}


def search(q):
    url = ("https://api.crossref.org/works?rows=3&select=DOI,title,container-title,issued,author,volume,page,type"
           "&query.bibliographic=" + urllib.parse.quote(q))
    r = urllib.request.Request(url, headers={"User-Agent": "ref-harvest/1.0 (mailto:%s)" % MAIL})
    with urllib.request.urlopen(r, timeout=45) as resp:
        return json.load(resp)["message"]["items"]


out = {}
for tag, q in QUERIES.items():
    try:
        items = search(q)
    except Exception as e:
        print("%-15s SEARCH FAILED %s" % (tag, e)); continue
    m = items[0]
    title = (m.get("title") or ["?"])[0]
    jr = (m.get("container-title") or ["?"])[0]
    yr = (m.get("issued", {}).get("date-parts") or [[None]])[0][0]
    auth = m.get("author") or []
    names = ["%s %s" % (a.get("family", "?"), "".join(w[0] for w in (a.get("given") or "").split()))
             for a in auth]
    out[tag] = {"doi": m["DOI"], "title": title, "journal": jr, "year": yr,
                "authors": names, "volume": m.get("volume"), "page": m.get("page"),
                "type": m.get("type")}
    print("%-15s %-42s %s (%s)\n%15s %s\n" % (tag, m["DOI"], jr[:40], yr, "", title[:80]))
    time.sleep(0.3)

json.dump(out, open("_refs_new.json", "w"), indent=1)
print("harvested %d" % len(out))
