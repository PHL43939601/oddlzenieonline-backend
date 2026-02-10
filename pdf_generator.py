#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Generator pre OddlženieOnline.sk
Generuje 4 dokumenty pre osobný bankrot - kompatibilné s HTML formulárom
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import json, sys, re
from datetime import datetime

try:
    pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
    FONT = 'DejaVuSans'
    FONT_BOLD = 'DejaVuSans-Bold'
except:
    FONT = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'

def esc(text):
    """Escape HTML special chars for ReportLab Paragraph"""
    if not text:
        return ''
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def format_date(text):
    """Convert YYYY-MM-DD to DD.MM.YYYY, leave other formats unchanged"""
    if not text:
        return ''
    text = str(text).strip()
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', text)
    if m:
        return f'{m.group(3)}.{m.group(2)}.{m.group(1)}'
    return text

class PDFGenerator:
    def __init__(self, data):
        self.data = data
        self.styles = self._create_styles()

    def g(self, key, default=''):
        """Get value from data safely"""
        val = self.data.get(key, default)
        if val is None:
            return default
        return str(val).strip() if val else default

    def _create_styles(self):
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='DocTitle', fontName=FONT_BOLD, fontSize=13,
            textColor=colors.HexColor('#1e293b'), spaceAfter=6, alignment=TA_CENTER, leading=16))
        styles.add(ParagraphStyle(name='DocSubtitle', fontName=FONT, fontSize=9,
            textColor=colors.HexColor('#475569'), spaceAfter=16, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='SectionH', fontName=FONT_BOLD, fontSize=10,
            textColor=colors.HexColor('#1e3a5f'), spaceAfter=8, spaceBefore=14))
        styles.add(ParagraphStyle(name='SubH', fontName=FONT_BOLD, fontSize=9,
            textColor=colors.HexColor('#334155'), spaceAfter=6, spaceBefore=8))
        styles.add(ParagraphStyle(name='Body', fontName=FONT, fontSize=9,
            textColor=colors.HexColor('#334155'), spaceAfter=4, leading=13))
        styles.add(ParagraphStyle(name='BodyBold', fontName=FONT_BOLD, fontSize=9,
            textColor=colors.HexColor('#1e293b'), spaceAfter=4, leading=13))
        styles.add(ParagraphStyle(name='Small', fontName=FONT, fontSize=8,
            textColor=colors.HexColor('#64748b'), spaceAfter=3, leading=11))
        styles.add(ParagraphStyle(name='Legal', fontName=FONT, fontSize=8,
            textColor=colors.HexColor('#475569'), spaceAfter=4, leading=12))
        return styles

    def _make_doc(self, filename):
        return SimpleDocTemplate(filename, pagesize=A4,
            rightMargin=2*cm, leftMargin=2*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)

    def _header_table(self):
        """Common header with debtor info"""
        data = [
            ['Meno:', esc(self.g('meno'))],
            ['Priezvisko:', esc(self.g('priezvisko'))],
            ['Titul:', esc(self.g('titul'))],
            ['Dátum narodenia:', esc(format_date(self.g('datumNarodenia')))],
            ['Rodné číslo:', esc(self.g('rodneCislo'))],
            ['Trvalé bydlisko:', esc(f"{self.g('ulica')} {self.g('cisloDomu')}, {self.g('psc')} {self.g('obec')}")],
        ]
        t = Table(data, colWidths=[5*cm, 11*cm])
        t.setStyle(TableStyle([
            ('FONT', (0,0),(0,-1), FONT_BOLD, 9),
            ('FONT', (1,0),(1,-1), FONT, 9),
            ('TEXTCOLOR', (0,0),(-1,-1), colors.HexColor('#1e293b')),
            ('VALIGN', (0,0),(-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0),(-1,-1), 4),
            ('TOPPADDING', (0,0),(-1,-1), 2),
        ]))
        return t

    def _field_table(self, rows):
        """Create a standard field table with text wrapping"""
        label_style = ParagraphStyle('TblLabel', fontName=FONT_BOLD, fontSize=9,
            textColor=colors.HexColor('#1e293b'), leading=12)
        value_style = ParagraphStyle('TblValue', fontName=FONT, fontSize=9,
            textColor=colors.HexColor('#1e293b'), leading=12)
        wrapped = []
        for r in rows:
            wrapped.append([Paragraph(str(r[0]), label_style), Paragraph(str(r[1]), value_style)])
        t = Table(wrapped, colWidths=[6*cm, 10*cm])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0),(-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0),(-1,-1), 5),
            ('TOPPADDING', (0,0),(-1,-1), 3),
            ('GRID', (0,0),(-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ]))
        return t

    def _item_header(self, text):
        """Colored header row for items"""
        t = Table([[text]], colWidths=[16*cm])
        t.setStyle(TableStyle([
            ('FONT', (0,0),(-1,-1), FONT_BOLD, 9),
            ('BACKGROUND', (0,0),(-1,-1), colors.HexColor('#e0e7ff')),
            ('TEXTCOLOR', (0,0),(-1,-1), colors.HexColor('#1e3a5f')),
            ('BOTTOMPADDING', (0,0),(-1,-1), 6),
            ('TOPPADDING', (0,0),(-1,-1), 6),
            ('LEFTPADDING', (0,0),(-1,-1), 8),
        ]))
        return t

    def _signature_block(self, story):
        today = datetime.now().strftime('%d.%m.%Y')
        story.append(Spacer(1, 1.2*cm))
        story.append(Paragraph(f'V __________________ , dňa {today}', self.styles['Body']))
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph('________________________________________', self.styles['Body']))
        story.append(Paragraph('Podpis dlžníka', self.styles['Body']))

    def _collect_dynamic(self, prefix):
        """Collect dynamic form fields by prefix into list of dicts.
        E.g. prefix='p' collects p_lv_0, p_obec_0, p_lv_1, p_obec_1 etc."""
        items = {}
        pattern = re.compile(f'^{re.escape(prefix)}_(.+?)_(\\d+)$')
        for key, val in self.data.items():
            m = pattern.match(key)
            if m:
                field_name = m.group(1)
                idx = int(m.group(2))
                if idx not in items:
                    items[idx] = {}
                items[idx][field_name] = val
        return [items[k] for k in sorted(items.keys())]

    # ============================================
    # DOKUMENT 1: ŽIVOTOPIS DLŽNÍKA
    # ============================================
    def generate_zivotopis(self, filename):
        doc = self._make_doc(filename)
        story = []

        story.append(Paragraph('Životopis dlžníka, aktuálna životná situácia', self.styles['DocTitle']))
        story.append(Paragraph('a zoznam spriaznených osôb', self.styles['DocTitle']))
        story.append(Paragraph('V súlade s § 167 ods. 2 a § 168 ods. 2 zákona č. 7/2005 Z. z. o konkurze a reštrukturalizácii', self.styles['DocSubtitle']))
        story.append(Spacer(1, 0.3*cm))

        # 1. Osobné údaje
        story.append(Paragraph('1. Osobné údaje dlžníka', self.styles['SectionH']))
        story.append(self._header_table())
        story.append(Spacer(1, 0.2*cm))

        # Kontakt
        story.append(Paragraph('Kontaktné údaje:', self.styles['SubH']))
        story.append(self._field_table([
            ['Telefónne číslo:', esc(self.g('telefon'))],
            ['E-mail:', esc(self.g('email'))],
        ]))

        # 2. Vzdelanie
        story.append(Paragraph('2. Vzdelanie dlžníka', self.styles['SectionH']))
        story.append(self._field_table([
            ['Najvyššie dosiahnuté vzdelanie:', esc(self.g('vzdelanie'))],
            ['Ukončené v roku:', esc(self.g('vzdelanieRok'))],
            ['Odbor:', esc(self.g('vzdelanieOdbor'))],
            ['Škola:', esc(self.g('vzdelanieSkaola'))],
            ['Ďalšie vzdelanie, rekvalifikácia:', esc(self.g('dalsieVzdelanie'))],
        ]))

        # 3. Schopnosti
        story.append(Paragraph('3. Schopnosti, znalosti a zručnosti dlžníka', self.styles['SectionH']))
        story.append(self._field_table([
            ['Jazykové znalosti:', esc(self.g('jazyky'))],
            ['Vodičský preukaz:', esc(f"{self.g('vodicak')}, typ: {self.g('vodicakTyp')}")],
        ]))

        # 4. Zdravotný stav
        story.append(Paragraph('4. Zdravotný stav dlžníka', self.styles['SectionH']))
        story.append(Paragraph(esc(self.g('zdravotnyStav', 'Neuvedené')), self.styles['Body']))

        # 5. Pracovné skúsenosti
        story.append(Paragraph('5. Pracovné skúsenosti dlžníka', self.styles['SectionH']))
        praca_items = self._collect_dynamic('praca')
        if praca_items:
            rows = [['Od – Do', 'Zamestnávateľ', 'Pracovná pozícia']]
            for p in praca_items:
                rows.append([
                    esc(f"{p.get('od','')} – {p.get('do','')}"),
                    esc(p.get('zamestnavatel', '')),
                    esc(p.get('pozicia', ''))
                ])
            t = Table(rows, colWidths=[4*cm, 6*cm, 6*cm])
            t.setStyle(TableStyle([
                ('FONT', (0,0),(-1,0), FONT_BOLD, 9),
                ('FONT', (0,1),(-1,-1), FONT, 9),
                ('BACKGROUND', (0,0),(-1,0), colors.HexColor('#e0e7ff')),
                ('GRID', (0,0),(-1,-1), 0.5, colors.HexColor('#e2e8f0')),
                ('VALIGN', (0,0),(-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0),(-1,-1), 5),
                ('TOPPADDING', (0,0),(-1,-1), 3),
            ]))
            story.append(t)
        else:
            story.append(Paragraph('Neuvedené', self.styles['Body']))

        # 6. Sociálne postavenie
        story.append(Paragraph('6. Sociálne postavenie dlžníka', self.styles['SectionH']))
        story.append(Paragraph('V súčasnosti som:', self.styles['SubH']))
        soc_map = {
            'soc_zamestanany': 'zamestnaný/á',
            'soc_szco': 'samostatne zárobkovo činná osoba',
            'soc_dochodok': 'poberateľ/-ka dôchodku',
            'soc_nezamestnany': 'dobrovoľne nezamestnaný/á',
            'soc_uchadzac': 'uchádzač/-ka o zamestnanie',
            'soc_davky': 'poberateľ/-ka sociálnych dávok',
            'soc_ine': 'iné',
        }
        for key, label in soc_map.items():
            checked = '☒' if self.g(key) else '☐'
            extra = ''
            if key == 'soc_szco' and self.g(key):
                extra = f'    IČO: {esc(self.g("ico"))}'
            elif key == 'soc_dochodok' and self.g(key):
                extra = f'    druh: {esc(self.g("dochodokDruh"))}'
            elif key == 'soc_davky' and self.g(key):
                extra = f'    druh: {esc(self.g("davkyDruh"))}'
            elif key == 'soc_ine' and self.g(key):
                extra = f'    {esc(self.g("inePostavenie"))}'
            story.append(Paragraph(f'{checked} {label}{extra}', self.styles['Body']))

        # Rodinný stav a BSM
        story.append(Spacer(1, 0.2*cm))
        story.append(self._field_table([
            ['Rodinný stav:', esc(self.g('rodinnyStav'))],
            ['BSM:', esc(self.g('bsm', 'Nie'))],
        ]))

        # 7. Životná situácia
        story.append(Paragraph('7. Opíšte v stručnosti Vašu aktuálnu životnú situáciu', self.styles['SectionH']))

        # Príjmy
        story.append(Paragraph('Moje príjmy:', self.styles['SubH']))
        prijem_items = self._collect_dynamic('prijem')
        if prijem_items:
            rows = [['Suma (€)', 'Zdroj']]
            for p in prijem_items:
                rows.append([esc(f"{p.get('suma','')} €"), esc(p.get('zdroj',''))])
            t = Table(rows, colWidths=[5*cm, 11*cm])
            t.setStyle(TableStyle([
                ('FONT',(0,0),(-1,0),FONT_BOLD,9),('FONT',(0,1),(-1,-1),FONT,9),
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e0e7ff')),
                ('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#e2e8f0')),
                ('BOTTOMPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),3),
            ]))
            story.append(t)

        # Výdavky
        story.append(Paragraph('Moje výdavky:', self.styles['SubH']))
        vydavky = [
            ['Bývanie (nájom, energie):', esc(f"{self.g('vydaj_byvanie','0')} €")],
            ['Strava:', esc(f"{self.g('vydaj_strava','0')} €")],
            ['Hygiena a ošatenie:', esc(f"{self.g('vydaj_hygiena','0')} €")],
            ['Zdravotná starostlivosť:', esc(f"{self.g('vydaj_zdravie','0')} €")],
            ['Starostlivosť o deti:', esc(f"{self.g('vydaj_deti','0')} €")],
            ['Poistné:', esc(f"{self.g('vydaj_poistne','0')} €")],
            ['Cestovné:', esc(f"{self.g('vydaj_cestovne','0')} €")],
            ['Splácanie dlhov:', esc(f"{self.g('vydaj_dlhy','0')} €")],
        ]
        story.append(self._field_table(vydavky))

        # Vznik dlhov
        story.append(Paragraph('Ako vznikli moje dlhy:', self.styles['SubH']))
        story.append(Paragraph(esc(self.g('vznikDlhov', 'Neuvedené')), self.styles['Body']))

        # 8. Spriaznené osoby
        story.append(Paragraph('8. Zoznam osôb spriaznených s dlžníkom', self.styles['SectionH']))

        # 8.1 Spoločná domácnosť
        story.append(Paragraph('8.1. Spoločnú domácnosť tvorím s týmito osobami:', self.styles['SubH']))
        dom_osoby = self._collect_dynamic('dom')
        if dom_osoby:
            for i, osoba in enumerate(dom_osoby, 1):
                story.append(self._item_header(f'Osoba č. {i}'))
                # Build social status string
                soc_parts = []
                soc_dom_map = {
                    'soc_zamestanany': 'zamestnaný/á',
                    'soc_szco': 'SZČO',
                    'soc_dochodok': 'poberateľ/-ka dôchodku',
                    'soc_nezamestnany': 'dobrovoľne nezamestnaný/á',
                    'soc_uchadzac': 'uchádzač/-ka o zamestnanie',
                    'soc_davky': 'poberateľ/-ka sociálnych dávok',
                    'soc_ine': 'iné',
                }
                for sk, sl in soc_dom_map.items():
                    if osoba.get(sk):
                        extra = ''
                        if sk == 'soc_szco':
                            ico_val = osoba.get('ico', '')
                            if ico_val:
                                extra = f' (IČO: {ico_val})'
                        elif sk == 'soc_dochodok':
                            druh = osoba.get('dochodokDruh', '')
                            if druh:
                                extra = f' ({druh})'
                        elif sk == 'soc_davky':
                            druh = osoba.get('davkyDruh', '')
                            if druh:
                                extra = f' ({druh})'
                        elif sk == 'soc_ine':
                            ine_val = osoba.get('ine', '')
                            if ine_val:
                                extra = f' ({ine_val})'
                        soc_parts.append(f'{sl}{extra}')
                soc_text = ', '.join(soc_parts) if soc_parts else '–'
                story.append(self._field_table([
                    ['Meno a priezvisko:', esc(osoba.get('meno', ''))],
                    ['Dátum narodenia:', esc(format_date(osoba.get('datnar', '')))],
                    ['Vzťah:', esc(osoba.get('vztah', ''))],
                    ['Sociálne postavenie:', esc(soc_text)],
                ]))
                story.append(Spacer(1, 0.15*cm))
        else:
            story.append(Paragraph('(žiadne osoby v domácnosti)', self.styles['Body']))

        # 8.2 Blízke osoby
        story.append(Paragraph('8.2. Blízke osoby mimo domácnosti:', self.styles['SubH']))
        blizke = self._collect_dynamic('blizka')
        if blizke:
            rows = [['Meno a priezvisko', 'Vzťah', 'Adresa']]
            for b in blizke:
                rows.append([esc(b.get('meno','')), esc(b.get('vztah','')), esc(b.get('adresa',''))])
            t = Table(rows, colWidths=[5.5*cm, 4*cm, 6.5*cm])
            t.setStyle(TableStyle([
                ('FONT',(0,0),(-1,0),FONT_BOLD,9),('FONT',(0,1),(-1,-1),FONT,9),
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e0e7ff')),
                ('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#e2e8f0')),
                ('BOTTOMPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),3),
            ]))
            story.append(t)
        else:
            story.append(Paragraph('Neuvedené', self.styles['Body']))

        # 8.3 Účasti v PO
        story.append(Paragraph('8.3. Kvalifikované účasti v právnických osobách:', self.styles['SubH']))
        story.append(Paragraph('a) Moje účasti:', self.styles['BodyBold']))
        story.append(Paragraph(esc(self.g('mojeUcasti', '(žiadne)')), self.styles['Body']))
        story.append(Paragraph('b) Účasti blízkych osôb:', self.styles['BodyBold']))
        story.append(Paragraph(esc(self.g('blizkeUcasti', '(žiadne)')), self.styles['Body']))

        # Čestné prehlásenie
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(
            'Čestne vyhlasujem, že som platobne neschopný/á, do tohto stavu som sa nepriviedol/a úmyselne, '
            'pri preberaní záväzkov som sa nespoliehal/a na to, že svoje dlhy budem riešiť oddlžením a nemám '
            'v úmysle poškodiť svojho/ich veriteľa/ov alebo zvýhodniť niektorého/ých veriteľa/ov.',
            self.styles['Legal']))
        story.append(Paragraph(
            'Čestne vyhlasujem, že na území Slovenskej republiky mám centrum hlavných záujmov.',
            self.styles['Legal']))
        story.append(Paragraph(
            'Čestne vyhlasujem, že všetky údaje uvedené v žiadosti sú pravdivé a úplné a som si vedomý/á '
            'právnych následkov v prípade úmyselného uvedenia nepravdivých alebo neúplných údajov.',
            self.styles['Legal']))

        self._signature_block(story)
        doc.build(story)
        return filename

    # ============================================
    # DOKUMENT 2: ZOZNAM MAJETKU
    # ============================================
    def generate_majetok(self, filename):
        doc = self._make_doc(filename)
        story = []

        story.append(Paragraph('Zoznam majetku dlžníka', self.styles['DocTitle']))
        story.append(Spacer(1, 0.3*cm))
        story.append(self._header_table())
        story.append(Spacer(1, 0.3*cm))

        # Pozemky
        story.append(Paragraph('Pozemok', self.styles['SectionH']))
        pozemky = self._collect_dynamic('p')
        if pozemky:
            for i, p in enumerate(pozemky, 1):
                story.append(self._item_header(f'Pozemok č. {i}'))
                reg = p.get('register', 'C')
                story.append(self._field_table([
                    ['List vlastníctva č.:', esc(p.get('lv',''))],
                    ['Obec:', esc(p.get('obec',''))],
                    ['Katastrálne územie:', esc(p.get('ku',''))],
                    ['Parcela č.:', esc(f"{p.get('parcela','')} (register {reg})")],
                    ['Výmera (m²):', esc(p.get('vymera',''))],
                    ['Druh pozemku:', esc(p.get('druh',''))],
                    ['Hodnota:', esc(f"{p.get('hodnota','')} €")],
                    ['Spoluvlastnícky podiel:', esc(p.get('podiel',''))],
                ]))
                story.append(Spacer(1, 0.2*cm))
        else:
            story.append(Paragraph('(žiadne)', self.styles['Body']))

        # Stavby
        story.append(Paragraph('Stavba', self.styles['SectionH']))
        stavby = self._collect_dynamic('s')
        if stavby:
            for i, s in enumerate(stavby, 1):
                story.append(self._item_header(f'Stavba č. {i}'))
                reg = s.get('register', 'C')
                story.append(self._field_table([
                    ['List vlastníctva č.:', esc(s.get('lv',''))],
                    ['Obec:', esc(s.get('obec',''))],
                    ['Katastrálne územie:', esc(s.get('ku',''))],
                    ['Súpisné číslo:', esc(s.get('supisne',''))],
                    ['Orientačné číslo:', esc(s.get('orient',''))],
                    ['Na pozemku parcelné číslo:', esc(f"{s.get('parcela','')} (register {reg})")],
                    ['Popis stavby:', esc(s.get('popis',''))],
                    ['Hodnota:', esc(f"{s.get('hodnota','')} €")],
                    ['Spoluvlastnícky podiel:', esc(s.get('podiel',''))],
                ]))
                story.append(Spacer(1, 0.2*cm))
        else:
            story.append(Paragraph('(žiadne)', self.styles['Body']))

        # Byty
        story.append(Paragraph('Byt a nebytový priestor', self.styles['SectionH']))
        byty = self._collect_dynamic('b')
        if byty:
            for i, b in enumerate(byty, 1):
                story.append(self._item_header(f'Byt č. {i}'))
                reg = b.get('register', 'C')
                story.append(self._field_table([
                    ['List vlastníctva č.:', esc(b.get('lv',''))],
                    ['Obec:', esc(b.get('obec',''))],
                    ['Katastrálne územie:', esc(b.get('ku',''))],
                    ['Vchod:', esc(b.get('vchod',''))],
                    ['Poschodie:', esc(b.get('poschodie',''))],
                    ['Číslo bytu:', esc(b.get('cislo',''))],
                    ['Súpisné číslo:', esc(b.get('supisne',''))],
                    ['Orientačné číslo:', esc(b.get('orient',''))],
                    ['Na pozemku parcelné číslo:', esc(f"{b.get('parcela','')} (register {reg})")],
                    ['Druh pozemku:', esc(b.get('druh',''))],
                    ['Popis stavby:', esc(b.get('popisStavby',''))],
                    ['Podiel na spoločných častiach:', esc(b.get('podielSpoloc',''))],
                    ['Popis bytu:', esc(b.get('popisBytu',''))],
                    ['Hodnota:', esc(f"{b.get('hodnota','')} €")],
                    ['Spoluvlastnícky podiel:', esc(b.get('podiel',''))],
                ]))
                story.append(Spacer(1, 0.2*cm))
        else:
            story.append(Paragraph('(žiadne)', self.styles['Body']))

        # Hnuteľné veci
        story.append(Paragraph('Hnuteľná vec', self.styles['SectionH']))
        hnutelne = self._collect_dynamic('h')
        if hnutelne:
            for i, h in enumerate(hnutelne, 1):
                story.append(self._item_header(f'Hnuteľná vec č. {i}'))
                story.append(self._field_table([
                    ['Popis:', esc(h.get('popis',''))],
                    ['Výrobné číslo / VIN:', esc(h.get('vin',''))],
                    ['Evidenčné číslo / ŠPZ:', esc(h.get('spz',''))],
                    ['Kde sa nachádza:', esc(h.get('kde',''))],
                    ['Hodnota:', esc(f"{h.get('hodnota','')} €")],
                ]))
                story.append(Spacer(1, 0.2*cm))
        else:
            story.append(Paragraph('(žiadne)', self.styles['Body']))

        # Účty
        story.append(Paragraph('Pohľadávka z účtu', self.styles['SectionH']))
        ucty = self._collect_dynamic('ucet')
        if ucty:
            for i, u in enumerate(ucty, 1):
                story.append(self._item_header(f'Účet č. {i}'))
                story.append(self._field_table([
                    ['Číslo účtu / IBAN:', esc(u.get('iban',''))],
                    ['Banka:', esc(u.get('banka',''))],
                    ['Zostatok:', esc(f"{u.get('zostatok','')} €")],
                ]))
                story.append(Spacer(1, 0.2*cm))
        else:
            story.append(Paragraph('(žiadne)', self.styles['Body']))

        # Iné
        story.append(Paragraph('Iná majetková hodnota', self.styles['SectionH']))
        story.append(Paragraph(esc(self.g('ineMajetkoveHodnoty', '(žiadne)')), self.styles['Body']))

        # Zabezpečovacie práva
        story.append(Paragraph('Zabezpečovacie práva k majetku', self.styles['SectionH']))
        story.append(Paragraph(esc(self.g('zabezpPrava', '(žiadne)')), self.styles['Body']))

        # Súdne spory
        story.append(Paragraph('Súdne spory súvisiace s majetkom', self.styles['SectionH']))
        story.append(Paragraph(esc(self.g('sudneSpory', 'nemám')), self.styles['Body']))

        # Obydlie
        story.append(Paragraph('Obydlie – nepostihnuteľná hodnota obydlia dlžníka', self.styles['SectionH']))
        obydlie_typ = self.g('obydlieTyp')
        if obydlie_typ == 'nevlastnim':
            story.append(Paragraph(
                '☒ Vyhlasujem, že nevlastním obývateľnú vec, ktorá by mohla byť v zozname majetku '
                'označená za obydlie.', self.styles['Body']))
        elif obydlie_typ == 'uplatnujem':
            obydlie_vyber = self.g('obydlieVyber')
            parts = obydlie_vyber.split('|') if obydlie_vyber else ['', '', '']
            typ_tabulky = parts[0] if len(parts) > 0 else ''
            cislo_polozky = parts[1] if len(parts) > 1 else ''
            popis_polozky = parts[2] if len(parts) > 2 else obydlie_vyber
            bsm_obydlie = self.g('obydlieBSM', 'Nie')
            story.append(Paragraph(
                f'☒ Uplatňujem si nepostihnuteľnú hodnotu obydlia na obývateľnú vec (obydlie) '
                f'uvedenú v tabuľke označenej ako <b>{esc(typ_tabulky)}</b>, '
                f'číslo položky <b>{esc(cislo_polozky)}</b>.', self.styles['Body']))
            if popis_polozky:
                story.append(Paragraph(f'Špecifikácia: {esc(popis_polozky)}', self.styles['Small']))
            story.append(Spacer(1, 0.15*cm))
            if bsm_obydlie == 'Áno':
                story.append(Paragraph(
                    'Označené obydlie <b>je</b> v bezpodielovom spoluvlastníctve manželov. '
                    'Nepostihnuteľná hodnota obydlia: 20 000 € (10 000 € pre každého z manželov).',
                    self.styles['Body']))
            else:
                story.append(Paragraph(
                    'Označené obydlie <b>nie je</b> v bezpodielovom spoluvlastníctve manželov. '
                    'Nepostihnuteľná hodnota obydlia: 10 000 €.',
                    self.styles['Body']))
        else:
            story.append(Paragraph('☐ Neuvedené', self.styles['Body']))

        # Záverečné vyhlásenia
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(
            'Vyhlasujem, že v súčasnosti vlastním majetok uvedený v prílohe.',
            self.styles['Legal']))
        story.append(Paragraph(
            'Vyhlasujem, že všetky údaje uvedené v zozname majetku sú pravdivé, úplné a som si vedomý '
            'právnych následkov v prípade úmyselného uvedenia nepravdivých alebo neúplných údajov.',
            self.styles['Legal']))

        self._signature_block(story)
        doc.build(story)
        return filename

    # ============================================
    # DOKUMENT 3: HISTÓRIA MAJETKU (3 roky)
    # ============================================
    def generate_majetok_historia(self, filename):
        doc = self._make_doc(filename)
        story = []

        story.append(Paragraph('Zoznam majetku väčšej hodnoty, ktorý dlžník', self.styles['DocTitle']))
        story.append(Paragraph('vlastnil v posledných troch rokoch', self.styles['DocTitle']))
        story.append(Spacer(1, 0.3*cm))
        story.append(self._header_table())
        story.append(Spacer(1, 0.3*cm))

        # Hist pozemky
        story.append(Paragraph('Pozemok', self.styles['SectionH']))
        hp = self._collect_dynamic('hp')
        if hp:
            for i, p in enumerate(hp, 1):
                story.append(self._item_header(f'Pozemok č. {i}'))
                reg = p.get('register', 'C')
                story.append(self._field_table([
                    ['List vlastníctva č.:', esc(p.get('lv',''))],
                    ['Obec:', esc(p.get('obec',''))],
                    ['Katastrálne územie:', esc(p.get('ku',''))],
                    ['Parcela č.:', esc(f"{p.get('parcela','')} (register {reg})")],
                    ['Výmera (m²):', esc(p.get('vymera',''))],
                    ['Druh pozemku:', esc(p.get('druh',''))],
                    ['Hodnota:', esc(f"{p.get('hodnota','')} €")],
                    ['Spoluvlastnícky podiel:', esc(p.get('podiel',''))],
                ]))
                story.append(Spacer(1, 0.2*cm))
        else:
            story.append(Paragraph('(žiadne)', self.styles['Body']))

        # Hist stavby
        story.append(Paragraph('Stavba', self.styles['SectionH']))
        hs = self._collect_dynamic('hs')
        if hs:
            for i, s in enumerate(hs, 1):
                story.append(self._item_header(f'Stavba č. {i}'))
                reg = s.get('register', 'C')
                story.append(self._field_table([
                    ['List vlastníctva č.:', esc(s.get('lv',''))],
                    ['Obec:', esc(s.get('obec',''))],
                    ['Katastrálne územie:', esc(s.get('ku',''))],
                    ['Súpisné číslo:', esc(s.get('supisne',''))],
                    ['Orientačné číslo:', esc(s.get('orient',''))],
                    ['Na pozemku parcelné číslo:', esc(f"{s.get('parcela','')} (register {reg})")],
                    ['Popis stavby:', esc(s.get('popis',''))],
                    ['Hodnota:', esc(f"{s.get('hodnota','')} €")],
                    ['Spoluvlastnícky podiel:', esc(s.get('podiel',''))],
                ]))
        else:
            story.append(Paragraph('(žiadne)', self.styles['Body']))

        # Hist byty
        story.append(Paragraph('Byt a nebytový priestor', self.styles['SectionH']))
        hb = self._collect_dynamic('hb')
        if hb:
            for i, b in enumerate(hb, 1):
                story.append(self._item_header(f'Byt č. {i}'))
                reg = b.get('register', 'C')
                story.append(self._field_table([
                    ['List vlastníctva č.:', esc(b.get('lv',''))],
                    ['Obec:', esc(b.get('obec',''))],
                    ['Katastrálne územie:', esc(b.get('ku',''))],
                    ['Vchod:', esc(b.get('vchod',''))],
                    ['Poschodie:', esc(b.get('poschodie',''))],
                    ['Číslo bytu:', esc(b.get('cislo',''))],
                    ['Súpisné číslo:', esc(b.get('supisne',''))],
                    ['Orientačné číslo:', esc(b.get('orient',''))],
                    ['Na pozemku parcelné číslo:', esc(f"{b.get('parcela','')} (register {reg})")],
                    ['Popis bytu:', esc(b.get('popisBytu',''))],
                    ['Hodnota:', esc(f"{b.get('hodnota','')} €")],
                    ['Spoluvlastnícky podiel:', esc(b.get('podiel',''))],
                ]))
        else:
            story.append(Paragraph('(žiadne)', self.styles['Body']))

        # Hist hnuteľné
        story.append(Paragraph('Hnuteľná vec', self.styles['SectionH']))
        hh = self._collect_dynamic('hh')
        if hh:
            for i, h in enumerate(hh, 1):
                story.append(self._item_header(f'Hnuteľná vec č. {i}'))
                story.append(self._field_table([
                    ['Popis:', esc(h.get('popis',''))],
                    ['VIN:', esc(h.get('vin',''))],
                    ['ŠPZ:', esc(h.get('spz',''))],
                    ['Kde sa nachádza:', esc(h.get('kde',''))],
                    ['Hodnota:', esc(f"{h.get('hodnota','')} €")],
                ]))
        else:
            story.append(Paragraph('(žiadne)', self.styles['Body']))

        # Iné
        story.append(Paragraph('Iné (cenné papiere, pohľadávky, účty)', self.styles['SectionH']))
        story.append(Paragraph(esc(self.g('histIne', '(žiadne)')), self.styles['Body']))

        # Zabezp. práva + spory
        story.append(Paragraph('Zabezpečovacie práva k majetku', self.styles['SectionH']))
        story.append(Paragraph(esc(self.g('histZabezp', '(žiadne)')), self.styles['Body']))
        story.append(Paragraph('Súdne spory súvisiace s majetkom', self.styles['SectionH']))
        story.append(Paragraph(esc(self.g('histSpory', '(žiadne)')), self.styles['Body']))

        # Prehlásenie
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(
            'Vyhlasujem, že všetky údaje uvedené v zozname majetku väčšej hodnoty, ktorý som vlastnil '
            'v posledných troch rokoch, sú pravdivé, úplné a som si vedomý právnych následkov v prípade '
            'úmyselného uvedenia nepravdivých alebo neúplných údajov.',
            self.styles['Legal']))

        self._signature_block(story)
        doc.build(story)
        return filename

    # ============================================
    # DOKUMENT 4: ZOZNAM VERITEĽOV
    # ============================================
    def generate_veritelia(self, filename):
        doc = self._make_doc(filename)
        story = []

        story.append(Paragraph('Zoznam veriteľov dlžníka', self.styles['DocTitle']))
        story.append(Spacer(1, 0.3*cm))
        story.append(self._header_table())
        story.append(Spacer(1, 0.3*cm))

        veritelia = self._collect_dynamic('ver')
        if veritelia:
            for i, v in enumerate(veritelia, 1):
                story.append(self._item_header(f'Veriteľ č. {i}'))
                story.append(self._field_table([
                    ['Názov / Meno:', esc(v.get('nazov',''))],
                    ['IČO / Dátum narodenia:', esc(v.get('ico',''))],
                    ['Ulica (trvalé bydlisko / sídlo):', esc(v.get('ulica',''))],
                    ['Súpisné číslo:', esc(v.get('supisne',''))],
                    ['Obec:', esc(v.get('obec',''))],
                    ['PSČ:', esc(v.get('psc',''))],
                    ['Štát:', esc(v.get('stat','SR'))],
                ]))
                story.append(Spacer(1, 0.2*cm))
        else:
            story.append(Paragraph('Žiadni veritelia neuvedení', self.styles['Body']))

        # Prehlásenie
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(
            'Vyhlasujem, že všetky údaje uvedené v zozname veriteľov sú pravdivé, úplné a že som si vedomý '
            'právnych následkov v prípade úmyselného uvedenia nepravdivých alebo neúplných údajov.',
            self.styles['Legal']))

        self._signature_block(story)
        doc.build(story)
        return filename

    def generate_all(self, output_dir='.'):
        meno = self.g('meno', 'Dlznik')
        priezvisko = self.g('priezvisko', 'Neznamy')
        files = {
            'zivotopis': f"{output_dir}/Zivotopis_{meno}_{priezvisko}.pdf",
            'majetok': f"{output_dir}/Majetok_{meno}_{priezvisko}.pdf",
            'historia': f"{output_dir}/Majetok_Historia_{meno}_{priezvisko}.pdf",
            'veritelia': f"{output_dir}/Veritelia_{meno}_{priezvisko}.pdf",
        }
        self.generate_zivotopis(files['zivotopis'])
        self.generate_majetok(files['majetok'])
        self.generate_majetok_historia(files['historia'])
        self.generate_veritelia(files['veritelia'])
        return files


if __name__ == '__main__':
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {'meno': 'Test', 'priezvisko': 'User', 'rodneCislo': '000000/0000',
                'datumNarodenia': '01.01.2000', 'email': 'test@test.sk', 'telefon': '+421900000000',
                'ulica': 'Testová', 'cisloDomu': '1', 'obec': 'Nitra', 'psc': '94901'}

    generator = PDFGenerator(data)
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '/tmp'
    files = generator.generate_all(output_dir)
    print("PDF dokumenty vygenerované:")
    for key, path in files.items():
        print(f"  {key}: {path}")
 
