# Program: HLS Player Simulator
# 
# Fuction: download ts sements according to the m3u8 playlist, including vod and live.
#
# Version: 0.3
#	*support query string
#	*better usage of regex
#	*connection exception handling
#
# Version: 0.2
#	*use urllib2 instead of httplib
#	*support cookie
#
# Date: 2012-12-14

# TODO:
#support keep-alive? 
#support configuration file
#support https
#support logging

import sys
import re
import time
import signal
import urllib2
import cookielib

from m3u8 import m3u8

print "####################"
print "HLS Player Simulator"
print "####################"
print

debug_enable = False
def debug_dump(description, data):
	if(debug_enable):
		print description,
		print data
		return

def is_full_url(url):
	if url.find("http://") != -1:
		return True
	else:
		return False
		
def parse_full_url(full_url):
	result = re.search(r'^http://(.*?)(/.*/)(.*m3u8.*$)', full_url)
	host = result.group(1)
	path = result.group(2)
	m3u8_name = result.group(3) #including query string if any
	return host, path, m3u8_name
	
def signal_handler(siganl, frame):
	print "You typed Ctrl+C, will exit!"
	sys.exit()

signal.signal(signal.SIGINT, signal_handler)

if len(sys.argv) != 2 or is_full_url(sys.argv[1]) == False:
	print "Usage: python hls-simulator.py http://url-to-m3u8"
	sys.exit()
else:
	m3u8_url = sys.argv[1]
	print "m3u8 url: " + m3u8_url
	print

host, path, m3u8_name = parse_full_url(m3u8_url)
debug_dump("host:", host)
debug_dump("path:", path)
debug_dump("m3u8_name:", m3u8_name)
	
go_on_play = True
last_sequence_num = -1
is_first_list = True
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
while go_on_play:
	print "try to fetch m3u8 playlist file..."
	print "http://" + host + path + m3u8_name

	resp_code = -1
	m3u8_data = ''
	try:
		conn = opener.open("http://" + host + path + m3u8_name)
		resp_code = conn.getcode()
		m3u8_data = conn.read()
		conn.close()
	except urllib2.HTTPError, e:
		resp_code = e.code
	debug_dump("response code:", resp_code)
	if resp_code == 200:
		m = m3u8(m3u8_data)
		m.process()
		#m.dump()
		if m.is_m3u8:
			debug_dump("m3u8 file content:", m3u8_data)
			print "got m3u8 playlist file"
			print
			if last_sequence_num < m.media_sequence:
				last_sequcen_num = m.media_sequence
			else:
				print "new coming m3u8 playlist not fresh, retry..."
				print
				continue
			if m.is_tses:
				print "number of ts segments in current m3u8 playlist: ", len(m.tses)
				if m.is_endlist and is_first_list:
					print "HLS type is VoD"
					is_first_list = False
				else:
					print "HLS type is Live"
				print
				for item in m.tses:
					play_time = item['extinf']
					ts_path = item['ts_path']
					print "try to fetch ts segment file..."
					print "http://" + host + path + ts_path
					try:
						conn = opener.open("http://" + host + path + ts_path)
						resp_code = conn.getcode()
						conn.close()
						print "got " + ts_path + " last for ", play_time, " seconds."
						print
						time.sleep(play_time) # to make life easier, we just sleep instead of play
					except urllib2.HTTPError, e:
						print "error happened, http response code:", e.code
						print "Quit!"
						go_on_play = False
						
				if m.is_endlist:
					print "Come to the end of playlist, no more data to play!"
					print "Quit Successfuly!"
					go_on_play = False
				else:
					print "try to update m3u8 playlist..."
			elif m.is_streams:
				print "m3u8 playlist consists streams, pick one to follow..."
				print
				stream = (m.streams[0])['stream_path']
				if is_full_url(stream):
					host, path, m3u8_name = parse_full_url(stream)
				elif stream.find('/') != -1: # need to update path realtive to current m3u8
					result = re.search(r".*/", stream)
					add_path = result.group(0)
					path += add_path
					result = re.search(r"[^/]*\.m3u8", stream)
					m3u8_name = result.group(0)
				else: 
					m3u8_name = stream
			else:
				print "No streams or tses exist, Quit!"
				go_on_play = False
		else:
			print "Not valid m3u8 playlist, Quit!"
			go_on_play = False
	else:
		print "error happened, http response code:", resp_code
		print "Quit!"
		go_on_play = False
