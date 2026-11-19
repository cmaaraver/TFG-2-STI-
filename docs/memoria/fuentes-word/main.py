import json, subprocess, re, os, sys
import c1, c2, c3, c4
from lib import doc, fotos, completar, titulos
N = "Memoria_TFG_Calidad_Agua_LoRaWAN"
doc.core_properties.title = "Sistema de telemetría LoRaWAN para la monitorización de la calidad del agua"
doc.core_properties.author = "Carlos Maraver Román y Rubén Trillo García"
doc.save(N + ".docx")
print(len(fotos), "fotos;", len(completar), "completar")
if len(sys.argv) > 1:   # primera pasada: sacar las páginas de cada título
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", N + ".docx"], capture_output=True)
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", N + ".pdf"], capture_output=True, text=True).stdout).group(1))
    pags = [subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), "-layout", N + ".pdf", "-"], capture_output=True, text=True).stdout for i in range(1, n + 1)]
    ent, desde = [], 1
    for niv, t in titulos:
        for i in range(desde, n):
            if any(l.strip() == t for l in pags[i].split("\n")):
                ent.append([niv, t, i + 1]); desde = i; break
        else:
            print("NO ENCONTRADO", t)
    json.dump(ent, open("toc.json", "w", encoding="utf8"), ensure_ascii=False)
    print(len(ent), "de", len(titulos), "titulos; paginas", n)
