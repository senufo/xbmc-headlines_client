# -*- coding: utf-8 -*-

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

REMOTE_DBG = False 

DATA_PATH = xbmc.translatePath( "special://profile/addon_data/script.headlines/")
if not os.path.exists(DATA_PATH): os.makedirs(DATA_PATH)

addon = xbmcaddon.Addon('script.headlines_client')

RssFeedsPath = xbmc.translatePath('special://userdata/RssFeeds.xml')
print "RssFeedsPath = %s " % RssFeedsPath
try:
    feedsTree = parse(RssFeedsPath)
except:
    print "Erreur self.feedsTree"
#Recupere la liste des flux dans RSSFeeds.xml
if feedsTree:
    #self.feedsList = self.getCurrentRssFeeds()
    feedsList = dict()
    sets = feedsTree.getElementsByTagName('set')
    for s in sets:
        setName = 'set'+s.attributes["id"].value
        print "SETNAME = %s " % setName
        feedsList[setName] = {'feedslist':list(), 'attrs':dict()}
        #get attrs
        for attrib in s.attributes.keys():
            feedsList[setName]['attrs'][attrib] = s.attributes[attrib].value
        #get feedslist
        feeds = s.getElementsByTagName('feed')
        for feed in feeds:
            feedsList[setName]['feedslist'].append({'url':feed.firstChild.toxml(), 'updateinterval':feed.attributes['updateinterval'].value})
     
print "feed 1  = %s " % feedsList['set7']['feedslist'][0]['url']
set = feedsList['set7']['feedslist'][0]['url']
#On recuper l'url et on la transforme en non de fichier
file = re.sub('^http://.*/','Rss-',set)
RssFeeds = '%s/%s' % (DATA_PATH,file)
print "file = %s " % RssFeeds

if (os.path.isfile('%s-headlines' % RssFeeds)):
    pkl_file = open(('%s-headlines' % RssFeeds), 'rb')
    headlines = pickle.load(pkl_file)
    pkl_file.close()
else:
    print "Erreur ouverture HEADLINES"
 
print repr(headlines[0][0])
print repr(headlines[0][1])
print repr(headlines[0][2])
print repr(headlines[0][3])
print repr(headlines[0][4])
print repr(headlines[0][5])

for arg in sys.argv:

    param = str(arg).lower()
    print "param = %s " % param
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
        feeds.append(param.replace('feed=', ''))
        NoSet = param.replace('feed=', '')
        
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
           
#    if param != 'script.headlines_client':
#        args = args + ',' + arg

print "FEED = %s, limit = %d " % (feeds , limit)
print "feed %d  = %s " % (int(NoSet),feedsList['set%s' %
                                              NoSet]['feedslist'][0]['url'])

okno = Window(xbmcgui.getCurrentWindowId())
print repr(headlines[0][0])
    
okno.setProperty('RSS.Title', headlines[0][0] )
okno.setProperty('RSS.Desc', headlines[0][2])


