# -*- coding: utf-8 -*-

import cherrypy
import os
import sys
import shutil
import xml.etree.ElementTree as et

MAGIOKIS_TOP = '/home/albert/magiokis'
MAGIOKIS_DATA = os.path.join(MAGIOKIS_TOP, 'data')
MAGIOKIS_ROOT = os.path.join(MAGIOKIS_DATA, "content")

sys.path.append(MAGIOKIS_TOP)
from magiokis_page import denkbank
sys.path.append(MAGIOKIS_DATA)
from pagehandler import make_xspf_objects, make_xspf_opn_page, make_xspf_pl_page
from pagehandler import make_tekst_page
sys.path.append(os.path.join(MAGIOKIS_DATA, "songs"))
from opname import Opname
from songtekst import Songtekst
from song import Song
import objectlists as ol
sys.path.append(os.path.join(MAGIOKIS_DATA, "vertel"))
from vertellers import Cats
from vertel_item import catlijst
sys.path.append(os.path.join(MAGIOKIS_DATA, "dicht"))
from dicht_trefw import jarenlijst

HERE = os.path.dirname(__file__)
PAGES = os.path.join(HERE, 'pages')
SECTIONS = ['OW', 'SpeelMee', 'Speel', 'Zing', 'Vertel',
            'Dicht', 'Act', 'Art', 'Denk', 'Bio']
STATIC = 'http://local.magiokis.nl'

class HomePage(object):
    def __init__(self):
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
        return open(os.path.join(PAGES,"index.html")).read()

class Page(object):

    def header(self):
        width_data = [71,66,64,68,75,83,86,74,76,76]
        lines = [
            '<?xml version="1.0" encoding="iso-8859-1"?>',
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '
                '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',
            '<html><head><title>{}_{}</title>'.format(self.section, self.subsection),
            '<link href="/style/magiokis.css" rel="stylesheet" type="text/css" />',
            ]
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
            with open(os.path.join(MAGIOKIS_ROOT, 'Denk', 'functions.js')) as f_in:
                lines.extend([line.replace('%cgipad%cgiprog?section=D',
                    '/d').replace('&subsection=S', '/s').replace('&trefwoord=',
                    '/').replace('&tekstnr=', '/') for line in f_in])
        lines.extend([
            '</head><body><div id="navtopbar">',
            '<img border="0" src="/images/TopBar_{}.gif" '.format(
                self.section),
            'width="750" height="40" usemap="#GetAround"  alt="Topbar" />',
            '<map name="GetAround" id="GetAround">',
            ])
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
        lines = ['<div id="left">']
        with open(os.path.join(PAGES,"{0}_navbar.html".format(self.section.lower()))) as f_in:
            for data in f_in:
                lines.append(data)
        lines.append('</div>')
        return lines

    def footer(self):
        return '</body></html>'

    def build(self, lines):
        data = self.header()
        data.extend(self.navbar())
        data.append('<div id="right" class="maxhi">')
        data.extend(lines)
        data.append('</div>')
        data.append(self.footer())
        return "".join(data)

    def get_flatpage(self, fn=""):
        if not fn:
            fn = os.path.join(MAGIOKIS_ROOT,
                self.section, self.subsection + ".html")
        data = self.header()
        data.extend(self.navbar())
        data.append('<div id="right" class="maxhi">')
        with open(fn) as f_in:
            for line in f_in:
                data.append(line)
        data.append('</div>')
        data.append(self.footer())
        return "".join(data).replace('%imagepad', '/images/')


class OldWhoresPage(Page):
    section = SECTIONS[0]

    @cherrypy.expose
    def index(self):
        self.subsection = 'Home'
        return self.get_flatpage()

    @cherrypy.expose
    def bio(self):
        self.subsection = 'Bio'
        return self.get_flatpage()

    @cherrypy.expose
    def default(self, album, track=''): # 1,2,12,3,4,5
        albumdata = {
                    '1': 'B 9A',
                    '2': 'B 9B',
                    '12': 'B11',
                    '3': 'B12',
                    '4': 'B13',
                    '5': 'B14'
                    }
        self.subsection = album
        x = ol.MemberList(albumdata[album], "opnameseries")
        if track:
            return self.build(make_xspf_opn_page(track))

        linkstr = '<td width="50%"><a href="/{0}/{1}/{2}/">{3}</a></td>'
        data = ['<p align="left">{0}<br />Recorded: {1}</p>'.format(x.titel,
                    x.tekst),
                '<table align="center" cellspacing="0" border="0" cellpadding=' \
                    '"4" width="90%">']
        h = len(x.lijst) / 2
        if h * 2 < len(x.lijst):
            h = h + 1
        linktekst = '<td width="50%"><a href="/ow/{}/{}/">{}</a></td>'
        for y in range(h):
            data.append('<tr>')
            data.append(linktekst.format(album, x.lijst[y], x.titels[y]))
            if y + h < len(x.lijst):
                data.append(linktekst.format(album, x.lijst[y+h], x.titels[y+h]))
            data.append('</tr>')
        data.append('</table>')
        return self.build(data)

class SpeelMeePage(Page):
    section = SECTIONS[1]

    def __init__(self):
        self.kramp = KrampPage()
        self.hans = MetHansPage()
        self.eye = EyePactPage()

    @cherrypy.expose
    def index(self):
        self.subsection = 'Contents'
        return self.get_flatpage()

class KrampPage(Page):
    section = SECTIONS[1]

    @cherrypy.expose
    def index(self):
        self.subsection = 'KrampOver'
        return self.get_flatpage()

    @cherrypy.expose
    def songs(self, song=""):
        self.subsection = 'KrampSongs'
        if song:
            return self.build(make_xspf_opn_page(song))
        fnaam = os.path.join(MAGIOKIS_ROOT, self.section, self.subsection + ".html")
        return self.get_flatpage()

    @cherrypy.expose
    def opnames(self):
        self.subsection = 'KrampOpnames'
        fnaam = os.path.join(MAGIOKIS_ROOT, self.section, self.subsection + ".html")
        return self.build(make_xspf_objects(fnaam)) #get_flatpage()

    @cherrypy.expose
    def fotos1(self):
        self.subsection = 'KrampFotos1'
        return self.get_flatpage()
    @cherrypy.expose
    def fotos2(self):
        self.subsection = 'KrampFotos2'
        return self.get_flatpage()
    @cherrypy.expose
    def fotos3(self):
        self.subsection = 'KrampFotos3'
        return self.get_flatpage()

class MetHansPage(Page):
    section = SECTIONS[1]

    @cherrypy.expose
    def index(self):
        self.subsection = 'HansdOver'
        return self.get_flatpage()

    @cherrypy.expose
    def songs(self, song=''):
        self.subsection = 'HansdSongs'
        if song:
            return self.build(make_xspf_opn_page(song))
        fnaam = os.path.join(MAGIOKIS_ROOT, self.section, self.subsection + ".html")
        return self.get_flatpage()

    @cherrypy.expose
    def opnames(self):
        self.subsection = 'HansdOpnames'
        fnaam = os.path.join(MAGIOKIS_ROOT, self.section, self.subsection + ".html")
        return self.build(make_xspf_objects(fnaam)) #get_flatpage()


class EyePactPage(Page):
    section = SECTIONS[1]

    @cherrypy.expose
    def index(self):
        self.subsection = 'EyePactOver'
        return self.get_flatpage()

    @cherrypy.expose
    def songs(self, song=''):
        self.subsection = 'EyePactSongs'
        if song:
            return self.build(make_xspf_opn_page(song))
        fnaam = os.path.join(MAGIOKIS_ROOT, self.section, self.subsection + ".html")
        return self.get_flatpage()

    @cherrypy.expose
    def opnames(self):
        self.subsection = 'EyePactOpnames'
        fnaam = os.path.join(MAGIOKIS_ROOT, self.section, self.subsection + ".html")
        return self.build(make_xspf_objects(fnaam)) #get_flatpage()

class SpeelPage(Page):
    section = SECTIONS[2]

    @cherrypy.expose
    def index(self):
        self.subsection = 'BestOf'
        return self.get_flatpage().replace(' <a href="', ' <a href="song/') # build(data)

    @cherrypy.expose
    def song(self, song=''):
        self.subsection = 'BestOf'
        return self.build(make_xspf_opn_page(song))

    @cherrypy.expose
    def fase(self, fase=''): # 0,1,2,3,4
        fasedict = {'0': "Begin",
                    '1': "Fase1",
                    '2': "Fase2",
                    '3': "Fase3",
                    '4': "Fase4",
                    }
        self.subsection = fasedict[fase]
        fn = os.path.join(MAGIOKIS_ROOT, self.section, self.subsection + ".html")
        if fase in ('0', '1', '2', '3'):
            return self.build(make_xspf_objects(fn))
        elif fase == '4':
            return self.get_flatpage().replace('%cgipad%cgiprog?section=S',
                '/s').replace('&amp;subsection=M', '/m')

    @cherrypy.expose
    def modules(self):
        self.subsection = 'Modules'
        fn = os.path.join(MAGIOKIS_ROOT, self.section, self.subsection + ".html")
        with open(fn) as fl:
            data = [x.replace('%xmldatapad', 'http://data.magiokis.nl/') for x in fl]
        return self.build(data)
      ## <page id="Modules" src="content/speel/Modules.html" action="fixlinks">Modules pagina</page>

class ZingPage(Page):
    section = SECTIONS[3]

    @cherrypy.expose
    def index(self):
        self.subsection = 'Contents'
        return self.get_flatpage()

    @cherrypy.expose
    def intro(self):
        self.subsection = 'Intro'
        return self.get_flatpage()

    @cherrypy.expose
    def jaar(self, jaar=''):
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
        regels = ["<div>%s</div>" % m.tekst,]
        for x in m.lijst: #
            ds = Song(x)
            if ds.found:
                regels.append('<a href="/zing/tekst/%s">%s</a> (%s) %s<br /'
                    '>' % (x, ds.songtitel, ds.datering, ds.commentaar))
        self.subsection = jaar
        return self.build(regels)

    @cherrypy.expose
    def default(self, subsection='tekst', songid=''):
        self.found = False
        regels = make_xspf_pl_page(songid)
        self.subsection = 'songtekst'
        return self.build(regels)

class VertelPage(Page):
    section = SECTIONS[4]

    @cherrypy.expose
    def index(self):
        self.subsection = 'Start'
        return self.get_flatpage()

    @cherrypy.expose
    def about(self):
        self.subsection = "About"
        return self.get_flatpage()

    @cherrypy.expose
    def bundel(self, bundel=''): # 1,2,3,4,5,0;
        dh = Cats("papa")
        ok = False
        for y in dh.categorieen:
            if y[1] == bundel:
                ok = True
                break
        if not ok:
            raise cherrypy.HTTPError(403)
        if bundel == "Langere":
            regels = ["<h3>hee, typisch, deze zijn geen van alle afgemaakt...</h3>",]
        else:
            regels = ["<br />",]
        regels.append('<div style="padding-left: 20%">')
        _, path, id_titels = catlijst("papa", bundel)
        for x in id_titels:
            regels.append('<a href="/vertel/verhaal/{}/{}">{}</a><br />'.format(
                bundel, '~'.join(os.path.split(x[2])), x[1]))
        regels.append('</div>')
        self.subsection = bundel
        return self.build(regels)

    @cherrypy.expose
    def default(self, subsection='verhaal', bundel='', itemid=''): # 1,2,3,4,5,0; afzonderlijk verhaal
        _, path, id_titels = catlijst("papa", bundel)
        if not bundel or not itemid:
            raise cherrypy.HTTPError(403)
        try:
            pad, naam = itemid.split('~')
        except ValueError:
            infile = os.path.join(path, itemid)
        else:
            infile = os.path.join(path, pad, naam)
        self.subsection = 'Verhaal'
        return self.build(make_tekst_page(infile))

class DichtPage(Page):
    section = SECTIONS[5]

    @cherrypy.expose
    def index(self):
        self.subsection = 'Start'
        return self.get_flatpage().replace('%cgipad%cgiprog?section=Dicht&amp;'
            'subsection=Start&amp;item=%dichtpadDicht_Sonnet.xml', '/dicht/sonnet/')

    @cherrypy.expose
    def sonnet(self):
        self.subsection = 'Sonnet'
        return self.get_flatpage()

    @cherrypy.expose
    def cover(self):
        self.subsection = 'Cover'
        return self.get_flatpage().replace('%cgipad%cgiprog?section=Dicht&amp;'
            'subsection=Inhoud', '/dicht/inhoud/')

    @cherrypy.expose
    def inhoud(self):
        self.subsection = 'Inhoud'
        return self.get_flatpage()

    @cherrypy.expose
    def default(self, subsection='jaar', jaar=''):
        infile = '/home/albert/magiokis/data/dicht/Dicht_{}.xml'.format(jaar)
        self.subsection = 'Jaarfile'
        return self.build(make_tekst_page(infile))

class ActeerPage(Page):
    section = SECTIONS[6]

    @cherrypy.expose
    def index(self):
        self.subsection = 'Contents'
        return self.get_flatpage()

    @cherrypy.expose
    def default(self, subsection='play', play=''): # 1,2,3,4
        shutil.copyfile('/home/albert/magiokis/data/acteer/{}.html'.format(play),
            os.path.join(MAGIOKIS_ROOT, 'Act', 'Play.html'))
        self.subsection = 'Play'
        return self.get_flatpage()

class ArtPage(Page):
    section = SECTIONS[7]

    @cherrypy.expose
    def index(self):
        self.subsection = 'Start'
        return self.get_flatpage().replace('%artpad', '/artwork/').replace(
            '%cgipad%cgiprog?section=Art&amp;subsection=S','/art/s')

    @cherrypy.expose
    def start2(self):
        self.subsection = 'Start2'
        return self.get_flatpage().replace('%artpad', '/artwork/')

    @cherrypy.expose
    def default(self, subject):
        self.subsection = subject
        return self.get_flatpage().replace('%artpad', '/artwork/').replace(
            '%cgipad%cgiprog?section=Art&amp;subsection=','/art/')

class DenkPage(Page):
    section = SECTIONS[8]

    @cherrypy.expose
    def index(self):
        self.subsection = 'start'
        return self.get_flatpage()

    @cherrypy.expose
    def select(self, trefwoord='', tekstnr=''): # dit is de denkbank
        self.subsection = 'select'
        if tekstnr:
            tekstnr = int(tekstnr)
        else:
            tekstnr = 0
        return self.build(x.decode('latin-1') + "\n" for x in denkbank(trefwoord, tekstnr))
    @cherrypy.expose
    def default(self,subject):
        self.subsection = subject
        return self.get_flatpage()

class BioPage(Page):
    section = SECTIONS[9]

    @cherrypy.expose
    def index(self):
        self.subsection = 'Start'
        return self.get_flatpage()

    @cherrypy.expose
    def default(self, subsection='subject', subject=''): # 1,2,3,4
        self.subsection = subject
        return self.get_flatpage()

root = HomePage()
cherrypy.tree.mount(root, config=os.path.join(HERE, 'magiokis.conf'))

if __name__ == '__main__':
    cherrypy.quickstart(config=os.path.join(HERE, 'magiokis.conf'))
