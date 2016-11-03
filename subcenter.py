# -*- coding: utf-8 -*-


import os
import sys
import xbmc
from xbmc import log
import urllib
import zipfile
import urllib2
import time
import uuid
import json
from unicodedata import normalize
import xbmcvfs
import re
import xbmcaddon
import xbmcgui
import xbmcplugin
import shutil
import unicodedata

__addon__ = xbmcaddon.Addon()
__author__     = __addon__.getAddonInfo('author')
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__    = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString

__cwd__        = xbmc.translatePath( __addon__.getAddonInfo('path') ).decode("utf-8")
__profile__    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) ).decode("utf-8")
__temp__       = xbmc.translatePath( os.path.join( __profile__, 'temp') ).decode("utf-8")

sys.path.append (__resource__)

def get_token():
    URLBASE=__addon__.getSetting("BASEURL")
    SUBUSER=__addon__.getSetting("USER")
    SUBPASS=__addon__.getSetting("PASSWORD")
    URL = URLBASE+"/he/api/login/"
    values = {'username' : SUBUSER,
              'password' : SUBPASS }
    data = urllib.urlencode(values)
    req = urllib2.Request(URL, data)
    response = urllib2.urlopen(req)
    the_page = json.loads(response.read())
    if 'token' not in the_page:
        dialog = xbmcgui.Dialog()
        dialog.notification('סאבסנטר ', 'אנא הרשמו באתר סאבסנטר ע"מ להשתמש בתוסף" .', xbmcgui.NOTIFICATION_INFO, 15000)
        time.sleep(15)
    else:
        dialog = xbmcgui.Dialog()
        dialog.notification('סאבסנטר ', 'אנא אל תשכחו להיכנס פעם ביום לאתר סאבנטר .', xbmcgui.NOTIFICATION_INFO, 10000)
    return(the_page)

def getEpisode(filename):
    match=re.findall(r"(?:s|season)(\d{2})", filename, re.I)
    if match:
        return str(match)



def Search(item):
    title_name=item['title']
    query=str(item['title']).replace("."," ").split("-")[0].split("720")[0].split("1080")[0].split("x264")[0].strip().replace("'",'')
    pattern = re.compile('\W')
    query=re.sub(pattern, ' ', query)
    the_page=get_token()
    URLBASE=__addon__.getSetting("BASEURL")
    print("QUERY: " + query)
    URL_SRCH=URLBASE+"/he/api/search/"
    if len(item['tvshow']) <1 and  getEpisode(title_name) is None:
        #incase of movies im stripping the year as subcenter does not take kindly to it.
        query_movie=re.split(r"(?:19|20)(\d{2})",query)[0]
        values1 = {'token' : the_page['token'],
            'user' : the_page['user'],
            'q' : query_movie,
            'type' : 'movies'	}
    else:
        if item['season']:
            season=item['season']
            episode=item['episode']
            titlestr=item['tvshow']
        else:
            season=re.findall(r"(?:s|season)(\d{2})", query, re.I)
            episode=re.findall(r"(?:e|x|episode|\n)(\d{2})", query, re.I)
            titlestr=re.split(r"(?:s|S|season|Season|SEASON)(\d{2})",query)[0]
        values1 = {'token' : the_page['token'],
            'user' : the_page['user'],
            'q' : titlestr,
            'type': 'series',
            'season': int(season[0]),
            'episode': int(episode[0])}
    data1 = urllib.urlencode(values1)
    req1 = urllib2.Request(URL_SRCH, data1)
    response1 = urllib2.urlopen(req1)
    sch_rst= json.loads(response1.read())
    log(str(sch_rst))
    if 'data' not in sch_rst:
        print("NO hits")
    else:
        for title in sch_rst['data']:
            for lang,subs in title['subtitles'].iteritems():
                if lang == 'en':
                    for sub in subs:
                        listitem = xbmcgui.ListItem(label="English",                                   # language name for the found subtitle
                                    label2=sub['version']+"srt",               # file name for the found subtitle
                                    iconImage=sub['downloads'],                                     # rating for the subtitle, string 0-5
                                    thumbnailImage="en.gif"                            # language flag, ISO_639_1 language + gif extention, e.g - "en.gif"
                                    )
                        if item['title'].replace(".","").replace(" ","").lower().find(sub['version'].replace(".","").replace(" ","").lower()) is -1:
                            listitem.setProperty( "sync",        '{0}'.format("false").lower() )
                        else:  # set to "true" if subtitle is matched by hash,
                            listitem.setProperty( "sync",        '{0}'.format("true").lower() )
                                                                                         # indicates that sub is 100 Comaptible
                        listitem.setProperty( "hearing_imp", '{0}'.format("false").lower() ) # set to "true" if subtitle is for hearing impared
                        url = "plugin://%s/?action=download&lang=%s&ID=%s&filename=%s&key=%s" % (__scriptid__,
                                                                                        lang,
                                                                                        sub['id'],
                                                                                        sub['version'],
                                                                                        sub['key']
                                                                                        )
                    ## add it to list, this can be done as many times as needed for all subtitles found
                        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)
                if lang == 'he':
                    for sub in subs:
                        listitem = xbmcgui.ListItem(label="Hebrew",                                   # language name for the found subtitle
                                label2=sub['version']+"srt",               # file name for the found subtitle
                                iconImage=sub['downloads'],                                     # rating for the subtitle, string 0-5
                                thumbnailImage="he.gif"                            # language flag, ISO_639_1 language + gif extention, e.g - "en.gif"
                                )
                        if item['title'].replace(".","").replace(" ","").lower().find(sub['version'].replace(".","").replace(" ","").lower()) is -1:
                            listitem.setProperty( "sync",        '{0}'.format("false").lower() )
                        else:  # set to "true" if subtitle is matched by hash,
                            listitem.setProperty( "sync",        '{0}'.format("true").lower() )
                        url = "plugin://%s/?action=download&lang=%s&ID=%s&filename=%s&key=%s" % (__scriptid__,
                                                                                        lang,
                                                                                        sub['id'],
                                                                                        sub['version'],
                                                                                        sub['key'])
                        ## add it to list, this can be done as many times as needed for all subtitles found
                        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=listitem,isFolder=False)


def Download(ID,lang,filename,key):
  URLBASE=__addon__.getSetting("BASEURL")
  url=URLBASE+"/he/api/subtitle/download/"+lang+"/?sub_id="+ID+"&v="+ urllib.quote(''.join(hex(ord(chr))[2:] for chr in filename), safe='')+"&key="+key
  subtitle_list = []
  if xbmcvfs.exists(__temp__):
     shutil.rmtree(__temp__)
  xbmcvfs.mkdirs(__temp__)
  the_page=get_token()
  values = {'token' : the_page['token'], 'user': the_page['user'] }
  data = urllib.urlencode(values)
  req = urllib2.Request(url, data)
  response = urllib2.urlopen(req)
  zipdata= response.read()
  log(url)
  log(data)
  zipfilename=os.path.join(__temp__,filename)
  output = open(zipfilename,'wb')
  output.write(zipdata)
  output.close()
  zfobj = zipfile.ZipFile(zipfilename)
  for subname in zfobj.namelist():
      if subname.find(".srt") >0:
          zfobj.extract(subname,__temp__)
          subtitle_list.append(os.path.join(__temp__,subname))



  return subtitle_list

def normalizeString(str):
  return unicodedata.normalize(
         'NFKD', unicode(unicode(str, 'utf-8'))
         ).encode('ascii','ignore')

def get_params():
  param=[]
  paramstring=sys.argv[2]
  if len(paramstring)>=2:
    params=paramstring
    cleanedparams=params.replace('?','')
    if (params[len(params)-1]=='/'):
      params=params[0:len(params)-2]
    pairsofparams=cleanedparams.split('&')
    param={}
    for i in range(len(pairsofparams)):
      splitparams={}
      splitparams=pairsofparams[i].split('=')
      if (len(splitparams))==2:
        param[splitparams[0]]=splitparams[1]
  return param
params = get_params()

if params['action'] in ['search', 'manualsearch']:
  if params['action'] == 'manualsearch':
      params['searchstring'] = urllib.unquote(params['searchstring'])
  item = {}
  item['temp']               = False
  item['rar']                = False
  item['year']               = xbmc.getInfoLabel("VideoPlayer.Year")                           # Year
  item['season']             = str(xbmc.getInfoLabel("VideoPlayer.Season"))                    # Season
  item['episode']            = str(xbmc.getInfoLabel("VideoPlayer.Episode"))                   # Episode
  item['tvshow']             = normalizeString(xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))   # Show
  item['title']              = normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle")) # try to get original title
  item['file_original_path'] = urllib.unquote(xbmc.Player().getPlayingFile().decode('utf-8'))  # Full path of a playing file
  item['3let_language']      = []
  if params['action'] == 'manualsearch':
      item['title']          =   params['searchstring']
  for lang in urllib.unquote(params['languages']).decode('utf-8').split(","):
    item['3let_language'].append(xbmc.convertLanguage(lang,xbmc.ISO_639_2))

  if item['title'] == "":
    item['title']  = normalizeString(xbmc.getInfoLabel("VideoPlayer.Title"))      # no original title, get just Title

  if item['episode'].lower().find("s") > -1:                                      # Check if season is "Special"
    item['season'] = "0"                                                          #
    item['episode'] = item['episode'][-1:]

  if ( item['file_original_path'].find("http") > -1 ):
    item['temp'] = True

  elif ( item['file_original_path'].find("rar://") > -1 ):
    item['rar']  = True
    item['file_original_path'] = os.path.dirname(item['file_original_path'][6:])

  elif ( item['file_original_path'].find("stack://") > -1 ):
    stackPath = item['file_original_path'].split(" , ")
    item['file_original_path'] = stackPath[0][8:]

  Search(item)

elif params['action'] == 'download':
  ## we pickup all our arguments sent from def Search()
  print(params)
  subs = Download(params['ID'],params['lang'],params['filename'],params['key'])
  ## we can return more than one subtitle for multi CD versions, for now we are still working out how to handle that in XBMC core
  for sub in subs:
    listitem = xbmcgui.ListItem(label=sub)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sub,listitem=listitem,isFolder=False)


xbmcplugin.endOfDirectory(int(sys.argv[1])) ## send end of directory to XBMC
