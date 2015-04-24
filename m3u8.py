# Program: m3u8 file parser
# 
# Fuction: parse the m3u8 playlist
#
# Version: 0.3
#
# Date: 2012-12-14
#
# Author: xingqi@cisco.com

import re

class m3u8(object):

	def __init__(self, data):
		self.data = data
		self.is_m3u8 = False
		self.is_endlist = False
		self.is_tses = False
		self.is_streams = False
		self.streams = []
		self.tses = []
		self.target_duration = 0
		self.media_sequence = 0
		
	def dump(self):
		#print self.data
		print "is_m3u8:", self.is_m3u8
		print "is_endlist:", self.is_endlist
		print "is_tses:", self.is_tses
		print "is_streams:", self.is_streams
		print "target_duration:", self.target_duration
		print "media_sequence:", self.media_sequence
		print "tses:", self.tses
		print "streams:", self.streams

	def process(self):
		delimiter = '\r\n'
		lines = self.data.split(delimiter)
		index = 0
		while index < len(lines):
			line = lines[index]
			if line.find("#EXTM3U") != -1:
				self.is_m3u8 = True;
			elif line.find("#EXT-X-TARGETDURATION") != -1:
				result = line.split(':')
				self.target_duration = int(result[1])
			elif line.find("#EXT-X-MEDIA-SEQUENCE") != -1:
				result = line.split(':')
				self.media_sequence = int(result[1])
			elif line.find("#EXT-X-ENDLIST") != -1:
				self.is_endlist = True
			elif line.find("#EXTINF") != -1: # tses
				result = re.search(r"\s*\d+", line)
				ts_dict = {}
				ts_dict['extinf'] = int(result.group(0))
				index += 1 # move to the next line
				line = lines[index]
				ts_dict['ts_path'] = line
				self.tses.append(ts_dict)
				continue
			elif line.find("#EXT-X-STREAM-INF") != -1: # streams
				stream_dict = {}
				result = re.search(r"PROGRAM-ID\s*=\s*(\d+)", line)
				stream_dict['program_id'] = int(result.group(1))
				result = re.search(r"BANDWIDTH\s*=\s*(\d+)", line)
				stream_dict['bandwidth'] = int(result.group(1))
				index += 1 # move to the next line
				line = lines[index]
				stream_dict['stream_path'] = line
				self.streams.append(stream_dict)
				continue
			index += 1
		if len(self.tses) > 0:
			self.is_tses = True
		elif len(self.streams) > 0:
			self.is_streams = True	
