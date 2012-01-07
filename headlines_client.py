# -*- coding: utf-8 -*-
import sys

import urllib, os.path, xbmc, re, htmlentitydefs, time

from xbmcgui import Window, WindowDialog
from xml.dom.minidom import parse, Document, _write_data, Node, Element
import pickle
import xbmcaddon
import xbmcgui, sys
#import rss
#from rss import ImageCacher, RSSFeedsListLoader, RSSReader, RSSSet, RSSSource, TimeZoneHandler

__addonID__  = "script.headlines_client"
__addon__    = xbmcaddon.Addon( __addonID__ )
__settings__ = __addon__
__addonDir__ = __settings__.getAddonInfo( "path" )

DEBUG = True 
#Importation du module headlines_parse du script headlines_daemon
settings_addonDaemon =  xbmcaddon.Addon( "service.headlines_daemon" )
addonDirDaemon = settings_addonDaemon.getAddonInfo( "path" )
sys.path.append(addonDirDaemon)
from headlines_parse import *

#Teste si le repertoire script.headlines existe
DATA_PATH = xbmc.translatePath( "special://profile/addon_data/script.headlines/")
if not os.path.exists(DATA_PATH): os.makedirs(DATA_PATH)


#Nettoie le code HTML d'après rssclient de xbmc
def htmlentitydecode(s):
    # code from http://snipplr.com/view.php?codeview&id=15261
    # First convert alpha entities (such as &eacute;)
    # (Inspired from http://mail.python.org/pipermail/python-list/2007-June/443813.html)
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
 
DATA_PATH = xbmc.translatePath( "special://profile/addon_data/script.headlines/")
if not os.path.exists(DATA_PATH): os.makedirs(DATA_PATH)

addon = xbmcaddon.Addon('script.headlines_client')

for arg in sys.argv:

    param = str(arg).lower()
    if DEBUG == True: print "[headlines_client]param = %s " % param
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
    if 'alarm=' in param:
        if 'true' in param:
            alarmEnabled = True
        elif 'false' in param:
            alarmEnabled = False   
    if 'onItemSelect=' in param:
        selectBuiltin = param.replace('onItemSelect=','')
    if param.startswith('prefix='):
        prefix = param.replace('prefix=', '')
        if not prefix.endswith('.'):
            prefix = prefix + '.'
    if 'feed=' in param:
        #feeds.append(param.replace('feed=', ''))
        NoSet = param.replace('feed=', '')
        RssFeeds = NoSet
        
    if 'limit=' in param:
        limit = int(param.replace('limit=', ''))
    if 'htmlimg=' in param:
        print 'htmlimg %s' % param
        if 'true' in param:
            includeHTMLsIMG = True
        elif 'false' in param:
            includeHTMLsIMG = False
            
    if 'imagecaching=' in param:
        if 'true' in param:
            imageCachingEnabled = True
        elif 'false' in param:
            imageCachingEnabled = False
            
    if 'forcemultithread=' in param:
        if 'true' in param:
            ForceMultiThread = True
        elif 'false' in param:
            ForceMultiThread = False       
           
headlines = []
filename = re.sub('^http://.*/','Rss-',RssFeeds)
filename = '%s/%s' % (DATA_PATH,filename)
if DEBUG == True: print "[headlines_client] => %s-headlines" % filename
if (os.path.isfile('%s-headlines' % filename)):
    if DEBUG == True: print "[headlines_client] 146"
    pkl_file = open(('%s-headlines' % filename), 'rb')
    headlines = pickle.load(pkl_file)
    pkl_file.close()
    if DEBUG == True: print "[headlines_client] 150"

else:
    if DEBUG == True: print "[headlines_client]Erreur ouverture HEADLINES"
    if DEBUG == True: print "[headlines_client]RSSFEED = %s, ,NoSet = %s, limit = %d " % (RssFeeds , NoSet, limit)
    RSStream = ParseRSS()
    RSStream.getRSS(RssFeeds)
    try:
        pkl_file = open(('%s-headlines' % RssFeeds), 'rb')
        headlines = pickle.load(pkl_file)
        pkl_file.close()
    except:
        headlines.append(('Indisponible',
                     'Indisponible','Indisponible','Indisponible','Indisponible','Indisponible'))
print '*' * 30
if DEBUG == True: print "[headlines_client]Feed= %s " % RssFeeds
print repr(headlines[0][0])
print repr(headlines[0][1])
print repr(headlines[0][2])
print repr(headlines[0][3])
print repr(headlines[0][4])
print repr(headlines[0][5])

okno = Window(xbmcgui.getCurrentWindowId())
print repr(headlines[0][0])
NbNews = len(headlines)
if limit > NbNews: limit = NbNews

for i in range(0,limit):
    
    okno.setProperty('RSS.%s.Title' % i , headlines[i][0] )
    okno.setProperty('RSS.%s.Date' % i , headlines[i][1])
    description = re.sub('(<[bB][rR][ /]>)|(<[/ ]*[pP]>)', '[CR]',
                                 headlines[i][2], re.DOTALL)
    html = cleanText(description)
    okno.setProperty('RSS.%s.Desc' % i , html)
    okno.setProperty('RSS.%s.Img' % i , headlines[i][4])
    okno.setProperty('RSS.%s.Video' % i , headlines[i][5])
    if DEBUG == True: print "[headlines_client]%i => %s " % (i,repr(headlines[i][0]))
    
