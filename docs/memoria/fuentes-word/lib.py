# Ayudas para montar el Word de la memoria con python-docx
import re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

AZUL = RGBColor(0x1F, 0x3A, 0x5F)
GRIS = RGBColor(0x55, 0x55, 0x55)

doc = Document()
fotos = []       # huecos de foto, para la lista final
completar = []   # datos por completar, para la lista final
_fig = [0]
_tab = [0]
_seccion = ['Portada']


def preparar():
    s = doc.sections[0]
    s.page_height, s.page_width = Cm(29.7), Cm(21.0)
    s.left_margin = s.right_margin = Cm(2.5)
    s.top_margin = s.bottom_margin = Cm(2.5)
    st = doc.styles['Normal']
    st.font.name = 'Calibri'
    st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Calibri')
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.line_spacing = 1.15
    for n, tam, antes in (('Heading 1', 18, 0), ('Heading 2', 14, 14), ('Heading 3', 12, 10)):
        h = doc.styles[n]
        h.font.name = 'Calibri'
        h.element.rPr.rFonts.set(qn('w:ascii'), 'Calibri')
        h.element.rPr.rFonts.set(qn('w:hAnsi'), 'Calibri')
        h.font.size = Pt(tam)
        h.font.bold = True
        h.font.color.rgb = AZUL
        h.paragraph_format.space_before = Pt(antes)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
    # Word actualiza el índice al abrir
    upd = OxmlElement('w:updateFields')
    upd.set(qn('w:val'), 'true')
    doc.settings.element.append(upd)


def _campo(par, instr, texto=''):
    r = par.add_run()
    a = OxmlElement('w:fldChar'); a.set(qn('w:fldCharType'), 'begin')
    i = OxmlElement('w:instrText'); i.set(qn('xml:space'), 'preserve'); i.text = instr
    b = OxmlElement('w:fldChar'); b.set(qn('w:fldCharType'), 'separate')
    t = OxmlElement('w:t'); t.text = texto
    c = OxmlElement('w:fldChar'); c.set(qn('w:fldCharType'), 'end')
    r._r.append(a)
    for e in (i, b, t, c):
        par.add_run()._r.append(e)
    return r


def cabecera_y_pie(texto):
    s = doc.sections[0]
    s.different_first_page_header_footer = True
    p = s.header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p.add_run(texto); r.font.size = Pt(10); r.font.color.rgb = GRIS
    f = s.footer.paragraphs[0]
    f.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _campo(f, 'PAGE', '1')


_marca = re.compile(r'(\*\*.+?\*\*|\[COMPLETAR[^\]]*\]|`[^`]+`)')


def _escribir(par, texto, tam=None, color=None, cursiva=False):
    for trozo in _marca.split(texto):
        if not trozo:
            continue
        if trozo.startswith('**'):
            r = par.add_run(trozo[2:-2]); r.bold = True
        elif trozo.startswith('[COMPLETAR'):
            r = par.add_run(trozo); r.font.highlight_color = WD_COLOR_INDEX.YELLOW
            completar.append((_seccion[0], trozo[1:-1].replace('COMPLETAR: ', '').replace('COMPLETAR', 'dato')))
        elif trozo.startswith('`'):
            r = par.add_run(trozo[1:-1]); r.font.name = 'Consolas'; r.font.size = Pt(10)
        else:
            r = par.add_run(trozo)
        if tam: r.font.size = Pt(tam)
        if color: r.font.color.rgb = color
        if cursiva: r.italic = True


def H(nivel, texto, salto=False):
    if salto:
        doc.add_page_break()
    if nivel <= 2:
        _seccion[0] = texto
        titulos.append((nivel, texto))
    return doc.add_heading(texto, level=nivel)


def P(texto, alin=None, **kw):
    p = doc.add_paragraph()
    if alin == 'c': p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif alin is None: p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    _escribir(p, texto, **kw)
    return p


def B(items):
    for it in items:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2)
        _escribir(p, it)


def N(items):
    for it in items:
        p = doc.add_paragraph(style='List Number')
        p.paragraph_format.space_after = Pt(2)
        _escribir(p, it)


def _sombra(celda, color):
    tcPr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), color)
    tcPr.append(shd)


def T(cab, filas, anchos=None, titulo=None, tam=9.5):
    if titulo:
        _tab[0] += 1
        p = doc.add_paragraph(); p.paragraph_format.keep_with_next = True
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(f'Tabla {_tab[0]}. '); r.bold = True; r.font.size = Pt(10)
        _escribir(p, titulo, tam=10)
    t = doc.add_table(rows=1, cols=len(cab))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, c in enumerate(cab):
        cel = t.rows[0].cells[i]
        cel.text = ''
        r = cel.paragraphs[0].add_run(c); r.bold = True; r.font.size = Pt(tam)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        _sombra(cel, '1F3A5F')
    # la fila de cabecera se repite si la tabla salta de página
    trPr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement('w:tblHeader'); th.set(qn('w:val'), 'true'); trPr.append(th)
    for n, fila in enumerate(filas):
        fila_n = t.add_row()
        fila_n._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
        cs = fila_n.cells
        for i, v in enumerate(fila):
            cs[i].text = ''
            par = cs[i].paragraphs[0]
            par.paragraph_format.space_after = Pt(0)
            par.paragraph_format.line_spacing = 1.0
            _escribir(par, str(v), tam=tam)
            if n % 2: _sombra(cs[i], 'F2F5F9')
    if not any(cab):
        t._tbl.remove(t.rows[0]._tr)
    if anchos:
        t.autofit = False
        for i, a_ in enumerate(anchos):
            t.columns[i].width = Cm(a_)
        for fila in t.rows:
            for i, a in enumerate(anchos):
                fila.cells[i].width = Cm(a)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def _pie(texto):
    _fig[0] += 1
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f'Figura {_fig[0]}. '); r.bold = True; r.font.size = Pt(10); r.font.color.rgb = GRIS
    r = p.add_run(texto); r.font.size = Pt(10); r.font.color.rgb = GRIS; r.italic = True
    return _fig[0]


def FIG(ruta, pie, ancho=16.0):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(ruta, width=Cm(ancho))
    _pie(pie)


def FOTO(desc, pie=None, alto=6.5):
    """Hueco para una foto: recuadro discontinuo con la descripción de lo que hay que poner."""
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.rows[0].cells[0]
    c.width = Cm(14)
    tcPr = c._tc.get_or_add_tcPr()
    b = OxmlElement('w:tcBorders')
    for lado in ('top', 'left', 'bottom', 'right'):
        e = OxmlElement(f'w:{lado}')
        e.set(qn('w:val'), 'dashed'); e.set(qn('w:sz'), '12'); e.set(qn('w:space'), '0'); e.set(qn('w:color'), '7F8FA6')
        b.append(e)
    tcPr.append(b)
    _sombra(c, 'F4F6FA')
    va = OxmlElement('w:vAlign'); va.set(qn('w:val'), 'center'); tcPr.append(va)
    trPr = t.rows[0]._tr.get_or_add_trPr()
    hh = OxmlElement('w:trHeight'); hh.set(qn('w:val'), str(int(alto * 567))); hh.set(qn('w:hRule'), 'atLeast')
    trPr.append(hh)
    cs = OxmlElement('w:cantSplit'); trPr.append(cs)
    p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    n = _fig[0] + 1
    r = p.add_run(f'[FOTO {len(fotos) + 1}]'); r.bold = True; r.font.size = Pt(13); r.font.color.rgb = RGBColor(0x7F, 0x8F, 0xA6)
    p2 = c.add_paragraph(); p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p2.add_run(desc); r.font.size = Pt(10); r.font.color.rgb = GRIS
    p3 = c.add_paragraph(); p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p3.add_run('(borrar este recuadro y pegar aquí la foto)'); r.font.size = Pt(8.5); r.italic = True
    r.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    sep = doc.add_paragraph(); sep.paragraph_format.space_after = Pt(0)
    sep.paragraph_format.line_spacing = 0.3
    num = _pie(pie or desc)
    fotos.append((len(fotos) + 1, num, _seccion[0], desc))


def COD(texto):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.line_spacing = 1.0
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd'); shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), 'F1F3F5')
    pPr.append(shd)
    lineas = texto.strip('\n').split('\n')
    for i, l in enumerate(lineas):
        r = p.add_run(l); r.font.name = 'Consolas'; r.font.size = Pt(9)
        r._r.rPr.rFonts.set(qn('w:eastAsia'), 'Consolas')
        if i < len(lineas) - 1:
            r.add_break()


def salto():
    doc.add_page_break()


titulos = []   # (nivel, texto) de cada título, para el índice


def indice():
    """Índice como campo TOC de Word, con las entradas ya escritas (toc.json) para que no salga vacío."""
    import json, os
    from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
    ent = json.load(open('toc.json', encoding='utf8')) if os.path.exists('toc.json') else []
    if not ent:
        p = doc.add_paragraph()
        _campo(p, 'TOC \\o "1-2" \\h \\z \\u', 'Actualizar campo para generar el índice.')
        return
    for k, (niv, txt, pag) in enumerate(ent):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(3 if niv == 2 else 5)
        p.paragraph_format.space_before = Pt(0 if niv == 2 else 6)
        p.paragraph_format.left_indent = Cm(0.7 if niv == 2 else 0)
        p.paragraph_format.tab_stops.add_tab_stop(Cm(16), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        if k == 0:
            r = p.add_run()
            a = OxmlElement('w:fldChar'); a.set(qn('w:fldCharType'), 'begin')
            i = OxmlElement('w:instrText'); i.set(qn('xml:space'), 'preserve'); i.text = 'TOC \\o "1-2" \\h \\z \\u'
            b = OxmlElement('w:fldChar'); b.set(qn('w:fldCharType'), 'separate')
            r._r.append(a)
            for e in (i, b): p.add_run()._r.append(e)
        r = p.add_run(f'{txt}\t{pag}'); r.bold = (niv == 1)
        if k == len(ent) - 1:
            r = p.add_run()
            c = OxmlElement('w:fldChar'); c.set(qn('w:fldCharType'), 'end'); r._r.append(c)
