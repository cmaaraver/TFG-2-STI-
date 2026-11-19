# Fuentes de la memoria en Word

Scripts en Python (python-docx) que generan `../Memoria_TFG_Calidad_Agua_LoRaWAN.docx`.

- `main.py` monta el documento con `c1.py` a `c4.py` (capítulos), `presu.py` (presupuesto) y `lib.py` (estilos y ayudas).
- `diag.py` crea los SVG de los planos 1, 2 y 5 y `r.js` los pasa a PNG con Playwright. Se lanzan dentro de `../planos/`:
  `cd ../planos && python3 ../fuentes-word/diag.py && node ../fuentes-word/r.js`.
  El plano 4 es una copia de `docs/img/instalacion-sensores.png` y el 3 de `docs/img/conexionado-simple.png`.
- `cap.js` saca las capturas de la web pública (`../capturas-web/`); `webdoc/` tiene esas capturas en JPG para el Word.

Para regenerar el Word (hace falta LibreOffice y `pdfinfo`/`pdftotext` para el índice):

```
cd docs/memoria/fuentes-word
python3 main.py 1     # primera pasada: calcula las páginas del índice (toc.json)
python3 main.py       # segunda pasada: Word definitivo
mv Memoria_TFG_Calidad_Agua_LoRaWAN.docx ..
```
