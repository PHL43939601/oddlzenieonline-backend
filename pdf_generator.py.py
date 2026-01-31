#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Generator pre OddlženieOnline.sk
Generuje všetky 4 dokumenty pre osobný bankrot
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import json
import sys
from datetime import datetime

# Registrácia Slovak fonts (ak sú dostupné)
# Pre produkciu použite DejaVu Sans alebo iný Unicode font
try:
    pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
    FONT = 'DejaVuSans'
    FONT_BOLD = 'DejaVuSans-Bold'
except:
    # Fallback na defaultné fonty
    FONT = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'


class PDFGenerator:
    """Hlavná trieda pre generovanie PDF dokumentov"""
    
    def __init__(self, data):
        """
        Args:
            data (dict): JSON údaje z formulára
        """
        self.data = data
        self.styles = self._create_styles()
    
    def _create_styles(self):
        """Vytvorenie custom štýlov pre PDF"""
        styles = getSampleStyleSheet()
        
        # Nadpis dokumentu
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontName=FONT_BOLD,
            fontSize=16,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        # Sekcia nadpis
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading1'],
            fontName=FONT_BOLD,
            fontSize=12,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=10,
            spaceBefore=15
        ))
        
        # Normálny text
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['BodyText'],
            fontName=FONT,
            fontSize=10,
            textColor=colors.HexColor('#334155'),
            spaceAfter=6
        ))
        
        # Label (bold)
        styles.add(ParagraphStyle(
            name='Label',
            parent=styles['BodyText'],
            fontName=FONT_BOLD,
            fontSize=10,
            textColor=colors.HexColor('#1e293b')
        ))
        
        return styles
    
    # ========================================
    # DOKUMENT 1: ŽIVOTOPIS
    # ========================================
    def generate_zivotopis(self, filename):
        """Generuje životopis dlžníka"""
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Nadpis
        story.append(Paragraph("ŽIVOTOPIS DLŽNÍKA", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        # Osobné údaje
        story.append(Paragraph("1. OSOBNÉ ÚDAJE", self.styles['SectionHeader']))
        
        osobne_udaje = [
            ["Meno a priezvisko:", f"{self.data.get('meno', '')} {self.data.get('priezvisko', '')}"],
            ["Rodné číslo:", self.data.get('rodneCislo', '')],
            ["Dátum narodenia:", self.data.get('datumNarodenia', '')],
            ["Miesto narodenia:", self.data.get('miestoNarodenia', '')],
            ["Štátna príslušnosť:", self.data.get('statnaPreslusnost', 'Slovenská republika')],
            ["Rodinný stav:", self.data.get('rodinnyStav', '')],
        ]
        
        table = Table(osobne_udaje, colWidths=[6*cm, 10*cm])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), FONT_BOLD, 10),
            ('FONT', (1, 0), (1, -1), FONT, 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.5*cm))
        
        # Trvalý pobyt
        story.append(Paragraph("2. TRVALÝ POBYT", self.styles['SectionHeader']))
        
        adresa_data = [
            ["Ulica a číslo:", f"{self.data.get('ulica', '')} {self.data.get('cislo', '')}"],
            ["Obec/Mesto:", self.data.get('obec', '')],
            ["PSČ:", self.data.get('psc', '')],
            ["Kraj:", self.data.get('kraj', '')],
        ]
        
        table2 = Table(adresa_data, colWidths=[6*cm, 10*cm])
        table2.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), FONT_BOLD, 10),
            ('FONT', (1, 0), (1, -1), FONT, 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(table2)
        story.append(Spacer(1, 0.5*cm))
        
        # Kontaktné údaje
        story.append(Paragraph("3. KONTAKTNÉ ÚDAJE", self.styles['SectionHeader']))
        
        kontakt_data = [
            ["Email:", self.data.get('email', '')],
            ["Telefón:", self.data.get('telefon', '')],
        ]
        
        table3 = Table(kontakt_data, colWidths=[6*cm, 10*cm])
        table3.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), FONT_BOLD, 10),
            ('FONT', (1, 0), (1, -1), FONT, 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(table3)
        story.append(Spacer(1, 0.5*cm))
        
        # Vzdelanie
        story.append(Paragraph("4. VZDELANIE", self.styles['SectionHeader']))
        story.append(Paragraph(
            self.data.get('vzdelanie', 'Stredoškolské vzdelanie'),
            self.styles['CustomBody']
        ))
        story.append(Spacer(1, 0.3*cm))
        
        # Zamestnanie
        story.append(Paragraph("5. ZAMESTNANIE A PRÍJEM", self.styles['SectionHeader']))
        
        zamest_data = [
            ["Súčasný stav:", self.data.get('zamestnanieStav', 'Zamestnaný')],
            ["Zamestnávateľ:", self.data.get('zamestnavatel', '')],
            ["Pozícia:", self.data.get('pozicia', '')],
            ["Mesačný príjem (netto):", f"{self.data.get('mesacnyPrijem', '0')} EUR"],
        ]
        
        table4 = Table(zamest_data, colWidths=[6*cm, 10*cm])
        table4.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), FONT_BOLD, 10),
            ('FONT', (1, 0), (1, -1), FONT, 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(table4)
        story.append(Spacer(1, 1*cm))
        
        # Podpis
        story.append(Paragraph("_" * 50, self.styles['CustomBody']))
        story.append(Paragraph("Dátum a podpis dlžníka", self.styles['CustomBody']))
        
        # Build PDF
        doc.build(story)
        return filename
    
    # ========================================
    # DOKUMENT 2: ZOZNAM MAJETKU
    # ========================================
    def generate_majetok(self, filename):
        """Generuje zoznam majetku"""
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Nadpis
        story.append(Paragraph("ZOZNAM MAJETKU DLŽNÍKA", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        # Údaje o dlžníkovi
        story.append(Paragraph(
            f"<b>Dlžník:</b> {self.data.get('meno', '')} {self.data.get('priezvisko', '')}",
            self.styles['CustomBody']
        ))
        story.append(Paragraph(
            f"<b>Rodné číslo:</b> {self.data.get('rodneCislo', '')}",
            self.styles['CustomBody']
        ))
        story.append(Spacer(1, 0.5*cm))
        
        # Nehnuteľnosti
        story.append(Paragraph("1. NEHNUTEĽNOSTI", self.styles['SectionHeader']))
        
        nehnutelnosti = self.data.get('nehnutelnosti', [])
        if nehnutelnosti:
            for i, neh in enumerate(nehnutelnosti, 1):
                neh_data = [
                    [f"Nehnuteľnosť #{i}"],
                    ["Typ:", neh.get('typ', '')],
                    ["Adresa:", neh.get('adresa', '')],
                    ["Podiel vlastníctva:", neh.get('podiel', '')],
                    ["Odhadovaná hodnota:", f"{neh.get('hodnota', '0')} EUR"],
                    ["Poznámka:", neh.get('poznamka', '')],
                ]
                
                table = Table(neh_data, colWidths=[6*cm, 10*cm])
                table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, 0), FONT_BOLD, 11),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e7ff')),
                    ('FONT', (0, 1), (0, -1), FONT_BOLD, 10),
                    ('FONT', (1, 1), (1, -1), FONT, 10),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                story.append(table)
                story.append(Spacer(1, 0.3*cm))
        else:
            story.append(Paragraph("Žiadne nehnuteľnosti", self.styles['CustomBody']))
        
        story.append(Spacer(1, 0.5*cm))
        
        # Motorové vozidlá
        story.append(Paragraph("2. MOTOROVÉ VOZIDLÁ", self.styles['SectionHeader']))
        
        vozidla = self.data.get('vozidla', [])
        if vozidla:
            for i, voz in enumerate(vozidla, 1):
                voz_data = [
                    [f"Vozidlo #{i}"],
                    ["Typ:", voz.get('typ', '')],
                    ["Značka/Model:", voz.get('znacka', '')],
                    ["ŠPZ:", voz.get('spz', '')],
                    ["Rok výroby:", voz.get('rok', '')],
                    ["Odhadovaná hodnota:", f"{voz.get('hodnota', '0')} EUR"],
                ]
                
                table = Table(voz_data, colWidths=[6*cm, 10*cm])
                table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, 0), FONT_BOLD, 11),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e7ff')),
                    ('FONT', (0, 1), (0, -1), FONT_BOLD, 10),
                    ('FONT', (1, 1), (1, -1), FONT, 10),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                story.append(table)
                story.append(Spacer(1, 0.3*cm))
        else:
            story.append(Paragraph("Žiadne motorové vozidlá", self.styles['CustomBody']))
        
        story.append(Spacer(1, 0.5*cm))
        
        # Bankové účty
        story.append(Paragraph("3. BANKOVÉ ÚČTY A SPORENIE", self.styles['SectionHeader']))
        
        ucty = self.data.get('bankyUcty', [])
        if ucty:
            for i, ucet in enumerate(ucty, 1):
                ucet_data = [
                    [f"Účet #{i}"],
                    ["Banka:", ucet.get('banka', '')],
                    ["Číslo účtu:", ucet.get('cislo', '')],
                    ["Zostatok:", f"{ucet.get('zostatok', '0')} EUR"],
                ]
                
                table = Table(ucet_data, colWidths=[6*cm, 10*cm])
                table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, 0), FONT_BOLD, 11),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e7ff')),
                    ('FONT', (0, 1), (0, -1), FONT_BOLD, 10),
                    ('FONT', (1, 1), (1, -1), FONT, 10),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                story.append(table)
                story.append(Spacer(1, 0.3*cm))
        else:
            story.append(Paragraph("Žiadne bankové účty", self.styles['CustomBody']))
        
        story.append(Spacer(1, 0.5*cm))
        
        # Iný majetok
        story.append(Paragraph("4. INÝ MAJETOK", self.styles['SectionHeader']))
        
        iny_majetok = self.data.get('inyMajetok', '')
        if iny_majetok:
            story.append(Paragraph(iny_majetok, self.styles['CustomBody']))
        else:
            story.append(Paragraph("Žiadny iný majetok", self.styles['CustomBody']))
        
        story.append(Spacer(1, 1*cm))
        
        # Celková hodnota
        celkova_hodnota = self.data.get('celkovaHodnotaMajetku', '0')
        story.append(Paragraph(
            f"<b>CELKOVÁ ODHADOVANÁ HODNOTA MAJETKU: {celkova_hodnota} EUR</b>",
            self.styles['SectionHeader']
        ))
        
        story.append(Spacer(1, 1*cm))
        
        # Podpis
        story.append(Paragraph("_" * 50, self.styles['CustomBody']))
        story.append(Paragraph("Dátum a podpis dlžníka", self.styles['CustomBody']))
        
        # Build PDF
        doc.build(story)
        return filename
    
    # ========================================
    # DOKUMENT 3: HISTÓRIA NADOBUDNUTIA MAJETKU
    # ========================================
    def generate_majetok_historia(self, filename):
        """Generuje históriu nadobudnutia majetku"""
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Nadpis
        story.append(Paragraph(
            "HISTÓRIA NADOBUDNUTIA A PREVODU MAJETKU",
            self.styles['CustomTitle']
        ))
        story.append(Spacer(1, 0.5*cm))
        
        # Údaje o dlžníkovi
        story.append(Paragraph(
            f"<b>Dlžník:</b> {self.data.get('meno', '')} {self.data.get('priezvisko', '')}",
            self.styles['CustomBody']
        ))
        story.append(Paragraph(
            f"<b>Rodné číslo:</b> {self.data.get('rodneCislo', '')}",
            self.styles['CustomBody']
        ))
        story.append(Spacer(1, 0.5*cm))
        
        story.append(Paragraph(
            "<b>Časové obdobie:</b> Posledných 5 rokov pred podaním návrhu",
            self.styles['CustomBody']
        ))
        story.append(Spacer(1, 0.5*cm))
        
        # História transakcií
        story.append(Paragraph("ZOZNAM TRANSAKCIÍ", self.styles['SectionHeader']))
        
        transakcie = self.data.get('historiaTransakcii', [])
        
        if transakcie:
            for i, trans in enumerate(transakcie, 1):
                trans_data = [
                    [f"Transakcia #{i}"],
                    ["Dátum:", trans.get('datum', '')],
                    ["Typ transakcie:", trans.get('typ', '')],
                    ["Predmet:", trans.get('predmet', '')],
                    ["Hodnota:", f"{trans.get('hodnota', '0')} EUR"],
                    ["Druhá strana:", trans.get('druhaStrana', '')],
                    ["Dôvod/Účel:", trans.get('dovod', '')],
                ]
                
                table = Table(trans_data, colWidths=[6*cm, 10*cm])
                table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, 0), FONT_BOLD, 11),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fef3c7')),
                    ('FONT', (0, 1), (0, -1), FONT_BOLD, 10),
                    ('FONT', (1, 1), (1, -1), FONT, 10),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                story.append(table)
                story.append(Spacer(1, 0.3*cm))
        else:
            story.append(Paragraph(
                "V posledných 5 rokoch neboli vykonané žiadne významné transakcie s majetkom.",
                self.styles['CustomBody']
            ))
        
        story.append(Spacer(1, 1*cm))
        
        # Čestné prehlásenie
        story.append(Paragraph("ČESTNÉ PREHLÁSENIE", self.styles['SectionHeader']))
        story.append(Paragraph(
            "Prehlasujem, že som uviedol všetky podstatné transakcie s majetkom "
            "za posledných 5 rokov pred podaním návrhu na vyhlásenie konkurzu. "
            "Uvedené údaje sú pravdivé a úplné.",
            self.styles['CustomBody']
        ))
        
        story.append(Spacer(1, 1*cm))
        
        # Podpis
        story.append(Paragraph("_" * 50, self.styles['CustomBody']))
        story.append(Paragraph("Dátum a podpis dlžníka", self.styles['CustomBody']))
        
        # Build PDF
        doc.build(story)
        return filename
    
    # ========================================
    # DOKUMENT 4: ZOZNAM VERITEĽOV
    # ========================================
    def generate_veritelia(self, filename):
        """Generuje zoznam veriteľov a záväzkov"""
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Nadpis
        story.append(Paragraph("ZOZNAM VERITEĽOV A ZÁVÄZKOV", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        # Údaje o dlžníkovi
        story.append(Paragraph(
            f"<b>Dlžník:</b> {self.data.get('meno', '')} {self.data.get('priezvisko', '')}",
            self.styles['CustomBody']
        ))
        story.append(Paragraph(
            f"<b>Rodné číslo:</b> {self.data.get('rodneCislo', '')}",
            self.styles['CustomBody']
        ))
        story.append(Spacer(1, 0.5*cm))
        
        # Zoznam veriteľov
        story.append(Paragraph("ZOZNAM VERITEĽOV", self.styles['SectionHeader']))
        
        veritelia = self.data.get('veritelia', [])
        
        if veritelia:
            for i, veritel in enumerate(veritelia, 1):
                ver_data = [
                    [f"Veriteľ #{i}"],
                    ["Názov/Meno:", veritel.get('nazov', '')],
                    ["Adresa:", veritel.get('adresa', '')],
                    ["IČO:", veritel.get('ico', 'Neuvedené')],
                    ["Typ záväzku:", veritel.get('typZavazku', '')],
                    ["Výška dlhu:", f"{veritel.get('vyskaD lhu', '0')} EUR"],
                    ["Zabezpečený dlh:", veritel.get('zabezpeceny', 'Nie')],
                    ["Poznámka:", veritel.get('poznamka', '')],
                ]
                
                table = Table(ver_data, colWidths=[6*cm, 10*cm])
                table.setStyle(TableStyle([
                    ('FONT', (0, 0), (-1, 0), FONT_BOLD, 11),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fee2e2')),
                    ('FONT', (0, 1), (0, -1), FONT_BOLD, 10),
                    ('FONT', (1, 1), (1, -1), FONT, 10),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                story.append(table)
                story.append(Spacer(1, 0.3*cm))
        else:
            story.append(Paragraph("Žiadni veritelia neuvedení", self.styles['CustomBody']))
        
        story.append(Spacer(1, 0.5*cm))
        
        # Celková suma dlhov
        celkovy_dlh = self.data.get('celkovyDlh', '0')
        story.append(Paragraph(
            f"<b>CELKOVÁ VÝŠKA ZÁVÄZKOV: {celkovy_dlh} EUR</b>",
            self.styles['SectionHeader']
        ))
        
        story.append(Spacer(1, 0.5*cm))
        
        # Rozdelenie dlhov
        story.append(Paragraph("ROZDELENIE ZÁVÄZKOV", self.styles['SectionHeader']))
        
        rozdelenie = [
            ["Zabezpečené záväzky:", f"{self.data.get('zabezpeceneDlhy', '0')} EUR"],
            ["Nezabezpečené záväzky:", f"{self.data.get('nezabezpeceneDlhy', '0')} EUR"],
            ["Exekúcie:", f"{self.data.get('pocetExekucii', '0')} ks"],
        ]
        
        table = Table(rozdelenie, colWidths=[8*cm, 8*cm])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), FONT_BOLD, 10),
            ('FONT', (1, 0), (1, -1), FONT, 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(table)
        
        story.append(Spacer(1, 1*cm))
        
        # Čestné prehlásenie
        story.append(Paragraph("ČESTNÉ PREHLÁSENIE", self.styles['SectionHeader']))
        story.append(Paragraph(
            "Prehlasujem, že som uviedol všetkých svojich veriteľov a všetky záväzky. "
            "Uvedené údaje sú pravdivé a úplné podľa môjho najlepšieho vedomia.",
            self.styles['CustomBody']
        ))
        
        story.append(Spacer(1, 1*cm))
        
        # Podpis
        story.append(Paragraph("_" * 50, self.styles['CustomBody']))
        story.append(Paragraph("Dátum a podpis dlžníka", self.styles['CustomBody']))
        
        # Build PDF
        doc.build(story)
        return filename
    
    def generate_all(self, output_dir='.'):
        """Generuje všetky 4 PDF dokumenty"""
        meno = self.data.get('meno', 'Dlznik')
        priezvisko = self.data.get('priezvisko', 'Neznamy')
        
        files = {
            'zivotopis': f"{output_dir}/Zivotopis_{meno}_{priezvisko}.pdf",
            'majetok': f"{output_dir}/Majetok_{meno}_{priezvisko}.pdf",
            'historia': f"{output_dir}/Majetok_Historia_{meno}_{priezvisko}.pdf",
            'veritelia': f"{output_dir}/Veritelia_{meno}_{priezvisko}.pdf",
        }
        
        try:
            self.generate_zivotopis(files['zivotopis'])
            self.generate_majetok(files['majetok'])
            self.generate_majetok_historia(files['historia'])
            self.generate_veritelia(files['veritelia'])
            
            return files
        except Exception as e:
            print(f"Chyba pri generovaní PDF: {e}", file=sys.stderr)
            raise


# ========================================
# MAIN - Použitie
# ========================================
if __name__ == '__main__':
    # Príklad testovacích dát
    test_data = {
        'meno': 'Ján',
        'priezvisko': 'Novák',
        'rodneCislo': '850315/1234',
        'datumNarodenia': '15.03.1985',
        'miestoNarodenia': 'Bratislava',
        'rodinnyStav': 'Ženatý',
        'ulica': 'Hlavná',
        'cislo': '123',
        'obec': 'Bratislava',
        'psc': '811 01',
        'kraj': 'Bratislavský',
        'email': 'jan.novak@email.sk',
        'telefon': '+421 901 234 567',
        'vzdelanie': 'Stredoškolské s maturitou',
        'zamestnanieStav': 'Zamestnaný',
        'zamestnavatel': 'ABC s.r.o.',
        'pozicia': 'Operátor',
        'mesacnyPrijem': '1200',
        'nehnutelnosti': [],
        'vozidla': [],
        'bankyUcty': [],
        'inyMajetok': 'Žiadny',
        'celkovaHodnotaMajetku': '0',
        'historiaTransakcii': [],
        'veritelia': [
            {
                'nazov': 'Banka XYZ',
                'adresa': 'Bankova 1, Bratislava',
                'ico': '12345678',
                'typZavazku': 'Úver',
                'vyskaDlhu': '15000',
                'zabezpeceny': 'Nie',
                'poznamka': 'Spotrebný úver'
            }
        ],
        'celkovyDlh': '15000',
        'zabezpeceneDlhy': '0',
        'nezabezpeceneDlhy': '15000',
        'pocetExekucii': '2'
    }
    
    # Ak sú dáta v JSON formáte z argumentu
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = test_data
    
    # Generovanie PDF
    generator = PDFGenerator(data)
    files = generator.generate_all('/tmp')
    
    print("PDF dokumenty vygenerované:")
    for key, path in files.items():
        print(f"  {key}: {path}")
