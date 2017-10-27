# -*- coding: utf-8 -*-
"""Magiokis implementatie met behulp van CherryPy
"""
import pathlib
import sys
import shutil
import io
## import xml.etree.ElementTree as et
import cherrypy

MAGIOKIS_BASE = pathlib.Path.home() / 'projects/magiokis'
MAGIOKIS_TOP = MAGIOKIS_BASE / 'main_logic'
MAGIOKIS_DATA = MAGIOKIS_BASE / 'dml'
MAGIOKIS_ROOT = pathlib.Path.home() / "magiokis/data/content"

sys.path.append(str(MAGIOKIS_TOP))
from magiokis_page import denkbank
sys.path.append(str(MAGIOKIS_DATA))
from pagehandler import make_xspf_objects, make_xspf_opn_page, make_xspf_pl_page
from pagehandler import make_tekst_page
sys.path.append(str(MAGIOKIS_DATA / "songs"))
## from opname import Opname
## from songtekst import Songtekst
from song import Song
import objectlists as ol
sys.path.append(str(MAGIOKIS_DATA / "vertel"))
from vertellers import Cats
from vertel_item import catlijst
## sys.path.append(MAGIOKIS_DATA / "dicht"))
## from dicht_trefw import jarenlijst

HERE = pathlib.Path(__file__).parent
PAGES = HERE / 'pages'
SECTIONS = ['OW', 'SpeelMee', 'Speel', 'Zing', 'Vertel',
            'Dicht', 'Act', 'Art', 'Denk', 'Bio']
STATIC = 'http://original.magiokis.nl'


class HomePage:
    """Class voor de landing page
    """
    def __init__(self):
        """mogelijke verbetering/versimpeling: moet dit in __init__ of zou het ook
        als class attributes kunnen?
        """
        self.ow = OldWhoresPage()
        self.speelmee = SpeelMeePage()
        self.speel = SpeelPage()
        self.zing = ZingPage()
        self.vertel = VertelPage()
        self.dicht = DichtPage()
        self.act = ActeerPage()
        self.art = ArtPage()
        self.denk = DenkPage()
        self.bio = BioPage()

    @cherrypy.expose
    def index(self):
        """view voor de landing page
        """
        data = []
        fn = PAGES / "index.html"
        if sys.version < '3':
            f_in = io.TextWrapper(fn.open(), encoding='utf-8')
        else:
            f_in = fn.open(encoding='utf-8')
        with f_in:
            for line in f_in:
                data.append(line)
        return data


class Page:
    """Basisfunctionaliteit voor de pagina's
    """
    def header(self):
        """stel de HTML header samen
        """
        width_data = [71, 66, 64, 68, 75, 83, 86, 74, 76, 76]
        lines = [
            '<!DOCTYPE html>',
            '<html><head><title>{}_{}</title>'.format(self.section, self.subsection),
            '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />',
            '<link href="{}/style/magiokis.css" '
            'rel="stylesheet" type="text/css" />'.format(STATIC)]
        if self.section in SECTIONS[0:4]:
            lines.append('<link href="{}/style/songtekst_html.css" '
                         'rel="stylesheet" type="text/css" />'.format(STATIC))
        elif self.section == SECTIONS[4]:
            lines.append('<link href="{}/style/vertel_html.css" '
                         'rel="stylesheet" type="text/css" />'.format(STATIC))
        elif self.section == SECTIONS[5]:
            lines.append('<link href="{}/style/dicht_html.css" '
                         'rel="stylesheet" type="text/css" />'.format(STATIC))
        elif self.section == SECTIONS[6]:
            lines.append('<link href="{}/style/toneelstuk_html.css" '
                         'rel="stylesheet" type="text/css" />'.format(STATIC))
        elif self.section == SECTIONS[8] and self.subsection == 'select':
            with (MAGIOKIS_ROOT / 'Denk' / 'functions.js').open() as f_in:
                lines.extend([line.replace(
                    '%cgipad%cgiprog?section=D', '/d').replace(
                        '&subsection=S', '/s').replace(
                            '&trefwoord=', '/').replace(
                                '&tekstnr=', '/') for line in f_in])
        lines.extend(['</head><body><div id="navtopbar">',
                      '<img border="0" src="{}/images/TopBar_{}.gif" '.format(
                          STATIC, self.section),
                      'width="750" height="40" usemap="#GetAround"  alt="Topbar" />',
                      '<map name="GetAround" id="GetAround">'])
        pos = 0
        for ix, name in enumerate(SECTIONS):
            line = "<!-- " if name == self.section else ''
            left = pos + 3
            right = left + width_data[ix]
            pos = right
            line += '<area shape="rect" coords="{0},1,{1},39"'.format(left, right)
            line += ' href="/{0}/" alt="naar {0}" />'.format(name.lower())
            if name == self.section:
                line += ' -->'
            lines.append(line)
        lines.append('<map></div><br/>')
        return lines

    def navbar(self):
        """stel de navigatielinks aan de linkerkant in
        """
        lines = ['<div id="left">']
        with (PAGES / "{}_navbar.html".format(self.section.lower())).open() as f_in:
            for data in f_in:
                lines.append(data)
        lines.append('</div>')
        return lines

    def footer(self):
        """sluit de HTML af
        """
        return '</body></html>'

    def build(self, lines):
        """bouw een dynamische pagina op
        """
        data = self.header()
        data.extend(self.navbar())
        data.append('<div id="right" class="maxhi">')
        data.extend(lines)
        data.append('</div>')
        data.append(self.footer())
        return "".join(data)

    def get_flatpage(self, fn=""):
        """bouw een platte pagina op
        """
        if not fn:
            fn = MAGIOKIS_ROOT / self.section / (self.subsection + ".html")
        data = self.header()
        data.extend(self.navbar())
        data.append('<div id="right" class="maxhi">')
        if sys.version < '3':
            f_in = io.TextWrapper(fn.open(), encoding='utf-8')
        else:
            f_in = fn.open(encoding='utf-8')
        with f_in:
            for line in f_in:
                data.append(line)
        data.append('</div>')
        data.append(self.footer())
        return "".join(data).replace('%imagepad', '{}/images/'.format(STATIC))


class OldWhoresPage(Page):
    """Class voor Pagina's in de Old Whores sectie
    """
    section = SECTIONS[0]

    @cherrypy.expose
    def index(self):
        """landing page van deze sectie
        """
        self.subsection = 'Home'
        return self.get_flatpage()

    @cherrypy.expose
    def bio(self):
        """bandbeschriving
        """
        self.subsection = 'Bio'
        return self.get_flatpage()

    @cherrypy.expose
    def default(self, album, track=''):
        """default view voor deze sectie (band pagina's)
        """
        albumdata = {'1': 'B 9A',
                     '2': 'B 9B',
                     '12': 'B11',
                     '3': 'B12',
                     '4': 'B13',
                     '5': 'B14'}
        self.subsection = album
        x = ol.MemberList(albumdata[album], "opnameseries")
        if track:
            return self.build(make_xspf_opn_page(track))

        data = ['<p align="left">{0}<br />Recorded: {1}</p>'.format(x.titel, x.tekst),
                '<table align="center" cellspacing="0" border="0" cellpadding='
                '"4" width="90%">']
        h = int(len(x.lijst) / 2)
        if h * 2 < len(x.lijst):
            h = h + 1
        linktekst = '<td width="50%"><a href="/ow/{}/{}/">{}</a></td>'
        for y in range(h):
            data.append('<tr>')
            data.append(linktekst.format(album, x.lijst[y], x.titels[y]))
            if y + h < len(x.lijst):
                data.append(linktekst.format(album, x.lijst[y + h], x.titels[y + h]))
            data.append('</tr>')
        data.append('</table>')
        return self.build(data)


class SpeelMeePage(Page):
    """Class voor Pagina's in de Muziek Met Anderen sectie
    """
    section = SECTIONS[1]

    def __init__(self):
        self.kramp = KrampPage()
        self.hans = MetHansPage()
        self.eye = EyePactPage()

    @cherrypy.expose
    def index(self):
        """landing page van deze subsectie
        """
        self.subsection = 'Contents'
        return self.get_flatpage()


class KrampPage(Page):
    """Class voor Pagina's in de Muziek met Anderen: Kramp subsectie
    """
    section = SECTIONS[1]

    @cherrypy.expose
    def index(self):
        """landing page van deze subsectie
        """
        self.subsection = 'KrampOver'
        return self.get_flatpage()

    @cherrypy.expose
    def songs(self, song=''):
        """lijst met Kramp songs
        """
        self.subsection = 'KrampSongs'
        if song:
            return self.build(make_xspf_opn_page(song))
        return self.get_flatpage()

    @cherrypy.expose
    def opnames(self):
        """Pagina met Kramp opnames
        """
        self.subsection = 'KrampOpnames'
        fnaam = str(MAGIOKIS_ROOT / self.section / (self.subsection + '.html'))
        return self.build(make_xspf_objects(fnaam))

    @cherrypy.expose
    def fotos1(self):
        """Eerste foto pagina
        """
        self.subsection = 'KrampFotos1'
        return self.get_flatpage()

    @cherrypy.expose
    def fotos2(self):
        """Tweede foto pagina
        """
        self.subsection = 'KrampFotos2'
        return self.get_flatpage()

    @cherrypy.expose
    def fotos3(self):
        """Derde foto pagina
        """
        self.subsection = 'KrampFotos3'
        return self.get_flatpage()


class MetHansPage(Page):
    """Class voor Pagina's in de Muziek met Anderen: Met Hans subsectie
    """
    section = SECTIONS[1]

    @cherrypy.expose
    def index(self):
        """landing page van deze subsectie
        """
        self.subsection = 'HansdOver'
        return self.get_flatpage()

    @cherrypy.expose
    def songs(self, song=''):
        """Lijst met songs
        """
        self.subsection = 'HansdSongs'
        if song:
            return self.build(make_xspf_opn_page(song))
        return self.get_flatpage()

    @cherrypy.expose
    def opnames(self):
        """Pagina met opnames
        """
        self.subsection = 'HansdOpnames'
        fnaam = str(MAGIOKIS_ROOT / self.section / (self.subsection + ".html"))
        return self.build(make_xspf_objects(fnaam))


class EyePactPage(Page):
    """Class voor Pagina's in de Muziek met Anderen: The Eye Pact subsectie
    """
    section = SECTIONS[1]

    @cherrypy.expose
    def index(self):
        """landing page van deze subsectie
        """
        self.subsection = 'EyePactOver'
        return self.get_flatpage()

    @cherrypy.expose
    def songs(self, song=''):
        """Lijst met songs
        """
        self.subsection = 'EyePactSongs'
        if song:
            return self.build(make_xspf_opn_page(song))
        return self.get_flatpage()

    @cherrypy.expose
    def opnames(self):
        """Pagina met opnames
        """
        self.subsection = 'EyePactOpnames'
        fnaam = str(MAGIOKIS_ROOT / self.section / (self.subsection + ".html"))
        return self.build(make_xspf_objects(fnaam))


class SpeelPage(Page):
    """Class voor Pagina's in de Muziek met Mijzelf sectie
    """
    section = SECTIONS[2]

    @cherrypy.expose
    def index(self):
        """landing page van deze sectie
        """
        self.subsection = 'BestOf'
        return self.get_flatpage().replace(' <a href="', ' <a href="song/')

    @cherrypy.expose
    def song(self, song):
        """Pagina met details van een "Best Of" song
        """
        self.subsection = 'BestOf'
        return self.build(make_xspf_opn_page(song))

    @cherrypy.expose
    def fase(self, fase):
        """Pagina met een aantal songs uit een bepaalde periode
        """
        fasedict = {'0': "Begin",
                    '1': "Fase1",
                    '2': "Fase2",
                    '3': "Fase3",
                    '4': "Fase4"}
        self.subsection = fasedict[fase]
        fnaam = str(MAGIOKIS_ROOT / self.section / (self.subsection + ".html"))
        if fase in ('0', '1', '2', '3'):
            return self.build(make_xspf_objects(fnaam))
        elif fase == '4':
            return self.get_flatpage().replace(
                '%cgipad%cgiprog?section=S', '/s').replace(
                    '&amp;subsection=M', '/m')

    @cherrypy.expose
    def modules(self):
        """Lijst met electronisch vastgelegde muziekjes
        """
        self.subsection = 'Modules'
        fnaam = MAGIOKIS_ROOT / self.section / (self.subsection + ".html")
        with fnaam.open() as fl:
            data = [x.replace('%xmldatapad', 'http://data.magiokis.nl/') for x in fl]
        return self.build(data)


class ZingPage(Page):
    """Class voor Pagina's in de Alle Liedjes sectie
    """
    section = SECTIONS[3]

    @cherrypy.expose
    def index(self):
        """landing page van deze sectie
        """
        self.subsection = 'Contents'
        return self.get_flatpage()

    @cherrypy.expose
    def intro(self):
        """titelpagina van een "Liedbundel"
        """
        self.subsection = 'Intro'
        return self.get_flatpage()

    @cherrypy.expose
    def jaar(self, jaar):
        """Lijst met liedjes geschreven in een bepaald jaar
        """
        try:
            m = ol.OwnerList('jaarseries')
        except ol.common.DataError as meld:
            return self.build(meld)
        if jaar not in m.lijst:
            raise cherrypy.HTTPError(403)

        try:
            m = ol.MemberList(int(jaar), "jaarseries")
        except ol.common.DataError as meld:
            return self.build(meld)
        regels = ['<div style="font-size: 0.7em">(let op: bij openen van een link'
                  ' kan de muziek meteen beginnen te spelen)</div>',
                  "<div>%s&nbsp;</div>" % m.tekst]
        for x in m.lijst:
            ds = Song(x)
            if ds.found:
                regels.append('<a href="/zing/titel/{}">{}</a> ({}) {}<br />'.format(
                    x, ds.songtitel, ds.datering, ds.commentaar))
        self.subsection = jaar
        return self.build(regels)

    @cherrypy.expose
    def titel(self, songid):
        """default view voor deze sectie: details van een liedje
        """
        self.found = False
        regels = make_xspf_pl_page(songid)
        self.subsection = 'songtekst'
        return self.build(regels)


class VertelPage(Page):
    """Class voor Pagina's in de Verhalen sectie
    """
    section = SECTIONS[4]

    @cherrypy.expose
    def index(self):
        """landing page van deze sectie
        """
        self.subsection = 'Start'
        return self.get_flatpage()

    @cherrypy.expose
    def about(self):
        """Pagina met beschrijving van deze categorie
        """
        self.subsection = "About"
        return self.get_flatpage()

    @cherrypy.expose
    def bundel(self, bundel):
        """Pagina met inhoudsopgave van een verzameling
        """
        dh = Cats("papa")
        ok = False
        for y in dh.categorieen:
            if y[1] == bundel:
                ok = True
                break
        if not ok:
            raise cherrypy.HTTPError(403)
        if bundel == "Langere":
            regels = ["<h3>hee, typisch, deze zijn geen van alle afgemaakt...</h3>"]
        else:
            regels = ["<br />"]
        regels.append('<div style="padding-left: 20%">')
        _, path, id_titels = catlijst("papa", bundel)
        for x in id_titels:
            path = pathlib.Path(x[2])
            regels.append('<a href="/vertel/{}/{}">{}</a><br />'.format(
                bundel, '~'.join((str(path.parent), path.name)), x[1]))
        regels.append('</div>')
        self.subsection = bundel
        return self.build(regels)

    @cherrypy.expose
    def default(self, bundel, itemid):
        """default view voor deze sectie: een verhaal zelf
        """
        _, path, id_titels = catlijst("papa", bundel)
        if not bundel or not itemid:
            raise cherrypy.HTTPError(403)
        try:
            pad, naam = itemid.split('~')
        except ValueError:
            infile = pathlib.Path(path) / itemid
        else:
            infile = pathlib.Path(path) / pad / naam
        self.subsection = 'Verhaal'
        return self.build(make_tekst_page(str(infile)))


class DichtPage(Page):
    """Class voor Pagina's in de Gedichten sectie
    """
    section = SECTIONS[5]

    @cherrypy.expose
    def index(self):
        """landing page van deze sectie
        """
        self.subsection = 'Start'
        return self.get_flatpage().replace(
            '%cgipad%cgiprog?section=Dicht&amp;subsection=Start&amp;item=%dichtpad'
            'Dicht_Sonnet.xml', '/dicht/sonnet/')

    @cherrypy.expose
    def sonnet(self):
        """Pagina met een sonnet dat ik ooit eens gemaakt heb
        """
        self.subsection = 'Sonnet'
        return self.get_flatpage()

    @cherrypy.expose
    def cover(self):
        """Omslag van een gedichtenbundel
        """
        self.subsection = 'Cover'
        return self.get_flatpage().replace(
            '%cgipad%cgiprog?section=Dicht&amp;subsection=Inhoud', '/dicht/inhoud/')

    @cherrypy.expose
    def inhoud(self):
        """achterflap van die gedichtenbundel
        """
        self.subsection = 'Inhoud'
        return self.get_flatpage()

    @cherrypy.expose
    def default(self, jaar):
        """default view voor deze sectie: gedichten uit een bepaald jaar
        """
        infile = MAGIOKIS_ROOT.parent / 'dicht/Dicht_{}.xml'.format(jaar)
        self.subsection = 'Jaarfile'
        return self.build(make_tekst_page(str(infile)))


class ActeerPage(Page):
    """Class voor Pagina's in de Toneelstukken sectie
    """
    section = SECTIONS[6]

    @cherrypy.expose
    def index(self):
        """landing page van deze sectie
        """
        self.subsection = 'Contents'
        return self.get_flatpage()

    @cherrypy.expose
    def play(self, play):
        """default view voor deze sectie: tekst van een toneelstuk
        """
        shutil.copyfile(str(MAGIOKIS_ROOT.parent / 'acteer/{}.html').format(play),
                       str(MAGIOKIS_ROOT / 'Act' / 'Play.html'))
        self.subsection = 'Play'
        return self.get_flatpage()


class ArtPage(Page):
    """Class voor Pagina's in de Strips en Tekeningen sectie
    """
    section = SECTIONS[7]

    @cherrypy.expose
    def index(self):
        """landing page van deze sectie
        """
        self.subsection = 'Start'
        return self.get_flatpage().replace('%artpad', '/artwork/').replace(
            '%cgipad%cgiprog?section=Art&amp;subsection=S', '/art/s')

    @cherrypy.expose
    def start2(self):
        """vervolg van de landing page
        """
        self.subsection = 'Start2'
        return self.get_flatpage().replace('%artpad', '/artwork/')

    @cherrypy.expose
    def default(self, subject):
        """default view voor deze sectie: een strip of tekening
        """
        self.subsection = subject
        return self.get_flatpage().replace('%artpad', '/artwork/').replace(
            '%cgipad%cgiprog?section=Art&amp;subsection=', '/art/')


class DenkPage(Page):
    """Class voor Pagina's in de Filosofie sectie
    """
    section = SECTIONS[8]

    @cherrypy.expose
    def index(self):
        """landing page van deze sectie
        """
        self.subsection = 'start'
        return self.get_flatpage()

    @cherrypy.expose
    def select(self, trefwoord='', tekstnr=''):
        """dit is de denkbank
        """
        self.subsection = 'select'
        if tekstnr:
            tekstnr = int(tekstnr)
        else:
            tekstnr = 0
        return self.build(x + "\n" for x in denkbank(trefwoord, tekstnr))  # .decode('latin-1')

    @cherrypy.expose
    def default(self, subject):
        """default view voor deze sectie: pagina's over zaken die mij aan het denken zetten
        """
        self.subsection = subject
        return self.get_flatpage()


class BioPage(Page):
    """Class voor pagina's in de Wie Ben Ik sectie
    """
    section = SECTIONS[9]

    @cherrypy.expose
    def index(self):
        """landing page van deze sectie
        """
        self.subsection = 'Start'
        return self.get_flatpage()

    @cherrypy.expose
    def subject(self, subject):
        """default view voor deze sectie: korte beschrijving van een fase
        """
        self.subsection = subject
        return self.get_flatpage()

root = HomePage()
cherrypy.tree.mount(root, config=str(HERE / 'magiokis.conf'))

if __name__ == '__main__':
    cherrypy.quickstart(config=str(HERE / 'magiokis_local.conf'))
