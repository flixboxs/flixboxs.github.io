#!/usr/bin/python                                                          #
# -*- coding: utf-8 -*-                                                    #
############################################################################
#							  /T /I										   #
#							   / |/ | .-~/								   #
#						   T\ Y	 I	|/	/  _							   #
#		  /T			   | \I	 |	I  Y.-~/							   #
#		 I l   /I		T\ |  |	 l	|  T  /								   #
#	  T\ |	\ Y l  /T	| \I  l	  \ `  l Y								   #
# __  | \l	 \l	 \I l __l  l   \   `  _. |								   #
# \ ~-l	 `\	  `\  \	 \ ~\  \   `. .-~	|								   #
#  \   ~-. "-.	`  \  ^._ ^. "-.  /	 \	 |								   #
#.--~-._  ~-  `	 _	~-_.-"-." ._ /._ ." ./								   #
# >--.	~-.	  ._  ~>-"	  "\   7   7   ]								   #
#^.___~"--._	~-{	 .-~ .	`\ Y . /	|								   #
# <__ ~"-.	~		/_/	  \	  \I  Y	  : |								   #
#	^-.__			~(_/   \   >._:	  | l______							   #
#		^--.,___.-~"  /_/	!  `-.~"--l_ /	   ~"-.						   #
#			   (_/ .  ~(   /'	  "~"--,Y	-=b-. _)					   #
#				(_/ .  \  Fire TV Guru/ l	   c"~o \					   #
#				 \ /	`.	  .		.^	 \_.-~"~--.	 )					   #
#				  (_/ .	  `	 /	   /	   !	   )/					   #
#				   / / _.	'.	 .':	  /		   '					   #
#				   ~(_/ .	/	 _	`  .-<_								   #
#					 /_/ . ' .-~" `.  / \  \		  ,z=.				   #
#					 ~( /	'  :   | K	 "-.~-.______//					   #
#					   "-,.	   l   I/ \_	__{--->._(==.				   #
#						//(		\  <	~"~"	 //						   #
#					   /' /\	 \	\	  ,v=.	((						   #
#					 .^. / /\	  "	 }__ //===-	 `						   #
#					/ / ' '	 "-.,__ {---(==-							   #
#				  .^ '		 :	T  ~"	ll								   #
#				 / .  .	 . : | :!		 \								   #
#				(_/	 /	 | | j-"		  ~^							   #
#				  ~-<_(_.^-~"											   #
#																		   #
############################################################################

#############################=IMPORTS=######################################
	#Kodi Specific
import xbmc,xbmcplugin,xbmcgui, xbmcaddon
	#Python Specific
import requests	
import xbmcvfs	
import os,re,sys,json,base64,shutil,socket
import urllib.request,urllib.parse,urllib.error,urllib.parse
from urllib.parse import urlparse
from urllib.request import Request, urlopen
	#Addon Specific
from . import control

##########################=VARIABLES=#######################################
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
GET_SET = xbmcaddon.Addon(ADDON_ID)
ADDON_NAME = ADDON.getAddonInfo("name")
ICON   = xbmcvfs.translatePath(os.path.join('special://home/addons/' + ADDON_ID,  'icon.png'))
DIALOG = xbmcgui.Dialog()
DP  = xbmcgui.DialogProgress()
COLOR1='white'
COLOR2='blue'
dns_text = GET_SET.getSetting(id='DNS')
f4m = GET_SET.getSetting(id='f4m')
Headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.5',
    'Content-Type': 'application/json',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Request': '1'
    }

def get_kversion():
    full_version_info = xbmc.getInfoLabel('System.BuildVersion')
    baseversion = full_version_info.split(".")
    intbase = int(baseversion[0])
    return intbase
   
def check_protocol(url):
	parsed = urlparse(dns_text)
	protocol = parsed.scheme
	if protocol=='https':
		return url.replace('http','https')
	else:
		return url

def log(msg):
	msg = str(msg)
	xbmc.log('%s-%s'%(ADDON_ID,msg),2)

def b64(obj):
	return base64.b64decode(obj).decode('utf-8')

def percentage(part, whole):
	return 100 * float(part)/float(whole)
	
def getInfo(label):
	try: return xbmc.getInfoLabel(label)
	except: return False
	
def LogNotify(title, message, times=2000, icon=ICON,sound=False):
	DIALOG.notification(title, message, icon, int(times), sound)
	
def ASln():
	return LogNotify("[COLOR {0}]{1}[/COLOR]".format(COLOR1, ADDON_ID), '[COLOR {0}]AdvancedSettings.xml have been written[/COLOR]'.format(COLOR2))

def regex_from_to(text, from_string, to_string, excluding=True):
	if excluding:
		try: r = re.search("(?i)" + from_string + "([\S\s]+?)" + to_string, text).group(1)
		except: r = ''
	else:
		try: r = re.search("(?i)(" + from_string + "[\S\s]+?" + to_string + ")", text).group(1)
		except: r = ''
	return r

def regex_get_all(text, start_with, end_with):
	r = re.findall("(?i)(" + start_with + "[\S\s]+?" + end_with + ")", text)
	return r
	
def regex_get_us(text, start_with, end_with):
	r = re.findall("(?i)(" + start_with + ".+?[UK: Sky Sports].+?" + end_with + ")", text)
	return r
	
def addDir(name,url,mode,iconimage,fanart,description):
	#u=sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)+"&iconimage="+urllib.parse.quote_plus(iconimage)+"&description="+urllib.parse.quote_plus(description)
	u = sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name.encode('utf-8', 'ignore'))+"&iconimage="+urllib.parse.quote_plus(iconimage)+"&description="+urllib.parse.quote_plus(str(description).encode('utf-8', 'ignore'))
	ok=True
	liz=xbmcgui.ListItem(name)
	liz.setArt({'icon':iconimage, 'thumb':iconimage})
	#liz.setInfo( type="Video", infoLabels={"Title": name,"Plot":description,})
	liz.setProperty('fanart_image', fanart)
	if mode==4:
		if get_kversion() > 19:
			info = liz.getVideoInfoTag()
			info.setTitle(name)
			info.setMediaType('video')
			info.setPlot(description)
		else:
			liz.setInfo( type="Video", infoLabels={"Title": name,"Plot":description})		
		if not f4m == "true":
			liz.setProperty("IsPlayable","true")
		ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
	elif mode==7 or mode==10 or mode==17 or mode==21:
		if get_kversion() > 19:
			info = liz.getVideoInfoTag()
			info.setTitle(name)
			info.setMediaType('video')
			info.setPlot(description)
		else:
			liz.setInfo( type="Video", infoLabels={"Title": name,"Plot":description})
		ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
	else:
		if get_kversion() > 19:
			info = liz.getVideoInfoTag()
			info.setTitle(name)
			info.setMediaType('video')
			info.setPlot(description)
		else:		
			liz.setInfo( type="Video", infoLabels={"Title": name,"Plot":description})
		ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok
	xbmcplugin.endOfDirectory

# meta	
def addDirMeta(name,url,mode,iconimage,fanart,description,year,cast,rating,runtime,genre):
	u = sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name.encode('utf-8', 'ignore'))+"&iconimage="+urllib.parse.quote_plus(iconimage)+"&description="+urllib.parse.quote_plus(str(description).encode('utf-8', 'ignore'))
	ok=True
	liz=xbmcgui.ListItem(name)
	liz.setArt({'icon':iconimage, 'thumb':iconimage})
	if get_kversion() > 19:
		info = liz.getVideoInfoTag()
		info.setTitle(name)
		info.setMediaType('video')
		info.setPlot(description)
		try:
			info.setRating(float(rating), 0, 'imdb')
		except:
			pass
		try:
			info.setYear(int(year))
		except:
			pass
		try:
			info.setDuration(int(runtime))
		except:
			pass
		try:
			info.setCast([str(cast)])
		except:
			pass
		try:
			info.setGenres([str(genre)])
		except:
			pass
	else:		
		liz.setInfo( type="Video", infoLabels={"Title": name,"Plot":description,"Rating":rating,"Year":year,"Duration":runtime,"Cast":cast,"Genre":genre})
	liz.setProperty('fanart_image', fanart)
	liz.setProperty("IsPlayable","true")
	cm = []
	cm.append(('Movie Information', 'XBMC.Action(Info)'))
	liz.addContextMenuItems(cm,replaceItems=True)
	if mode==19 or mode==20:
		ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	else:
		ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
	return ok

def OPEN_URL(url):
    xbmc.executebuiltin('Notification(%s)'%(url))
    response=requests.get(url,timeout=200, headers=Headers)
   
    data = response.json()

    
   
    return data   

def clear_cache():
	xbmc.log('CLEAR CACHE ACTIVATED')
	xbmc_cache_path = os.path.join(xbmcvfs.translatePath('special://home'), 'cache')
	confirm=xbmcgui.Dialog().yesno("Confirmação","Por favor confirme se você deseja apagar o cache do Kodi")
	if confirm:
		if os.path.exists(xbmc_cache_path)==True:
			for root, dirs, files in os.walk(xbmc_cache_path):
				file_count = 0
				file_count += len(files)
				if file_count > 0:
						for f in files:
							try:
								os.unlink(os.path.join(root, f))
							except:
								pass
						for d in dirs:
							try:
								shutil.rmtree(os.path.join(root, d))
							except:
								pass
		LogNotify("[COLOR {0}]{1}[/COLOR]".format(COLOR1, ADDON_NAME), '[COLOR {0}]Cache Limpo com Sucesso![/COLOR]'.format(COLOR2))
		xbmc.executebuiltin("Container.Refresh()")

def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
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

def getlocalip():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('8.8.8.8', 0))
	s = s.getsockname()[0]
	return s

def getexternalip():
	import json 
	url = urllib.request.urlopen("https://api.ipify.org/?format=json")
	data = json.loads(url.read().decode())
	return str(data["ip"])

def MonthNumToName(num):
	if '01' in num:
		month = 'Janeiro'
	elif '02' in num:
		month = 'Fevereiro'
	elif '03' in num:
		month = 'Março'
	elif '04' in num:
		month = 'Abril'
	elif '05' in num:
		month = 'Maio'
	elif '06' in num:
		month = 'Junho'
	elif '07' in num:
		month = 'Julho'
	elif '08' in num:
		month = 'Agosto'
	elif '09' in num:
		month = 'Setembro'
	elif '10' in num:
		month = 'Outubro'
	elif '11' in num:
		month = 'Novembro'
	elif '12' in num:
		month = 'Dezembro'
	return month

def killxbmc():
	killdialog = xbmcgui.Dialog().yesno('Force Close Kodi', '[COLOR white]You are about to close Kodi', 'Would you like to continue?[/COLOR]', nolabel='[B][COLOR red] No Cancel[/COLOR][/B]',yeslabel='[B][COLOR green]Force Close Kodi[/COLOR][/B]')
	if killdialog:
		os._exit(1)
	# else:
	# 	home()

def gen_m3u(url, path):
	parse = json.loads(OPEN_URL(url))
	i=1
	DP.create(ADDON_NAME, "Please Wait")
	with open (path, 'w+', encoding="utf-8") as ftg:
		ftg.write('#EXTM3U\n')
		for items in parse['available_channels']:
			a = parse['available_channels'][items]
			
			if a['stream_type'] == 'live':
				
				b = '#EXTINF:-1 channel-id="{0}" tvg-id="{1}" tvg-name="{2}" tvg-logo="{3}" channel-id="{4}" group-title="{5}",{6}'.format(i, a['epg_channel_id'], a['epg_channel_id'], a['stream_icon'], a['name'], a['category_name'], a['name'])
				
				if parse['server_info']['server_protocol'] == 'https':
					port = parse['server_info']['https_port']
				else:
					port = parse['server_info']['port']
				
				dns = '{0}://{1}:{2}'.format(parse['server_info']['server_protocol'], parse['server_info']['url'], port)
				c = '{0}/{1}/{2}/{3}'.format(dns, parse['user_info']['username'], parse['user_info']['password'],a['stream_id'])
				ftg.write(b+'\n'+c+'\n')
				i +=1
				DP.update(int(100), 'Found Channel \n' + a['name'] + '\n')
				if DP.iscanceled(): break
		DP.close
		DIALOG.ok(ADDON_NAME, 'Found ' + str(i) + ' Channels')

def keypopup(heading):
	kb =xbmc.Keyboard ('', 'heading', True)
	kb.setHeading(heading)
	kb.setHiddenInput(False)
	kb.doModal()
	if (kb.isConfirmed()):
		text = kb.getText()
		return text
	else:
		return False