# -*- coding: utf-8 -*-
import os.path, xbmc, re, htmlentitydefs, time

from xbmcgui import Window, WindowDialog
import pickle
import xbmcaddon
import xbmcgui, sys

__addonID__  = "script.headlines_client"
__addon__    = xbmcaddon.Addon( __addonID__ )
__settings__ = __addon__
__addonDir__ = __settings__.getAddonInfo( "path" )

DEBUG_LOG = __addon__.getSetting( 'debug' )
if 'true' in DEBUG_LOG : DEBUG_LOG = True
else: DEBUG_LOG = False

#Importation du module headlines_parse du script headlines_daemon
settings_addonDaemon =  xbmcaddon.Addon( "service.headlines_daemon" )
addonDirDaemon = settings_addonDaemon.getAddonInfo( "path" )
sys.path.append(addonDirDaemon)
from headlines_parse import *

#Teste si le repertoire script.headlines existe
DATA_PATH = xbmc.translatePath( 
    "special://profile/addon_data/script.headlines/")
if not os.path.exists(DATA_PATH): os.makedirs(DATA_PATH)

#Function Debug
def debug(msg):
    """
    print message if DEBUG_LOG == True
    """
    if DEBUG_LOG == True: print " [%s] : %s " % (__addonID__, msg)

#Nettoie le code HTML d'après rssclient de xbmc
def htmlentitydecode(s):
    # code from http://snipplr.com/view.php?codeview&id=15261
    # First convert alpha entities (such as &eacute;)
    # (Inspired from 
    #http://mail.python.org/pipermail/python-list/2007-June/443813.html)
    def entity2char(m):
        entity = m.group(1)
        if entity in htmlentitydefs.name2codepoint:
            return unichr(htmlentitydefs.name2codepoint[entity])
        return u" "  # Unknown entity: We replace with a space.
    
    t = re.sub(u'&(%s);' % u'|'.join(htmlentitydefs.name2codepoint),
               entity2char, s)
  
    # Then convert numerical entities (such as &#233;)
    t = re.sub(u'&#(\d+);', lambda x: unichr(int(x.group(1))), t)
   
    # Then convert hexa entities (such as &#x00E9;)
    return re.sub(u'&#x(\w+);', lambda x: unichr(int(x.group(1),16)), t)

def cleanText(txt):
    p = re.compile(r'\s+')
    txt = p.sub(' ', txt)
    
    txt = htmlentitydecode(txt)
    
    p = re.compile(r'<[^<]*?/?>')
    return p.sub('', txt)

#Path où sont stockés les flux 
DATA_PATH = xbmc.translatePath( 
    "special://profile/addon_data/script.headlines/")
if not os.path.exists(DATA_PATH): os.makedirs(DATA_PATH)

addon = xbmcaddon.Addon('script.headlines_client')
debug('HEADLINES CLIENT')

#Recupère les arguments envoyés par le skin qui a lancé le script
for arg in sys.argv:

    param = str(arg).lower()
    debug("param = %s " % param)
    if 'window' == param:
        isWindow = True
        ID = -1
    elif 'window=' in param:
        isWindow = True
        ID = int(param.replace('window=', ''))
    elif 'dialog' == param:
        isWindow = False
        ID = -1
    elif 'dialog=' in param:
        isWindow = False
        ID = int(param.replace('dialog=', ''))
    if 'feed=' in param:
        #feeds.append(param.replace('feed=', ''))
        RssFeeds = param.replace('feed=', '')
        
    if 'limit=' in param:
        limit = int(param.replace('limit=', ''))
    if 'htmlimg=' in param:
        print 'htmlimg %s' % param
        if 'true' in param:
            includeHTMLsIMG = True
        elif 'false' in param:
            includeHTMLsIMG = False
           
headlines = []
#Récupère l'url du flux et le change en nom de fichier
filename = re.sub('^http://.*/', 'Rss-', RssFeeds)
filename = '%s/%s' % (DATA_PATH, filename)
debug("=> %s-headlines" % filename)
#Si il existe on l'ouvre
if (os.path.isfile('%s-headlines' % filename)):
    pkl_file = open(('%s-headlines' % filename), 'rb')
    headlines = pickle.load(pkl_file)
    pkl_file.close()
#Sinon on appelle la Class ParsRSS pour le parser puis le sauver sur disque
else:
    debug("Erreur ouverture HEADLINES")
    RSStream = ParseRSS()
    RSStream.getRSS(RssFeeds)
    try:
        #On essaye d'ouvrir le fichier avec les news parser
        pkl_file = open(('%s-headlines' % RssFeeds), 'rb')
        headlines = pickle.load(pkl_file)
        pkl_file.close()
    except:
        #Si il n'est pas encore récupéré, on crée une news avec INDISPONIBLE
        headlines.append(('Indisponible', 'Indisponible', 
                          'Indisponible','Indisponible',
                          'Indisponible','Indisponible'))

debug("Feed= %s " % RssFeeds)

#On récupère l'ID de la fenêtre de skin qui à lancer le script
okno = Window(xbmcgui.getCurrentWindowId())
#Nb de news dans le flux
NbNews = len(headlines)
#Si il est > à la limite demandée, on ne récupére que limit
if limit > NbNews: limit = NbNews

for i in range(0, limit):
    #On défini les Properties 
    okno.setProperty('RSS.%s.Title' % i , headlines[i][0] )
    okno.setProperty('RSS.%s.Date' % i , headlines[i][1])
    description = re.sub('(<[bB][rR][ /]>)|(<[/ ]*[pP]>)', '[CR]',
                                 headlines[i][2], re.DOTALL)
    #On nettoie le code HTML
    html = cleanText(description)
    okno.setProperty('RSS.%s.Desc' % i , html)
    okno.setProperty('RSS.%s.Img' % i , headlines[i][4])
    okno.setProperty('RSS.%s.Video' % i , headlines[i][5])
    debug("%i => %s " % (i, repr(headlines[i][0])))
