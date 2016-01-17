#!/usr/bin/python

import sys
import struct
import collections

ENC_TABLE_PLATFORM = {
	0 : "Unicode/Generic",
	1 : "Macintosh - Use of this is discouraged...",
	2 : "Reserved - Do not use!",
	3 : "Microsoft"
}

ENC_TABLE_PLAT_SPECIFIC_ID = {
	0 : {
		0 : "Default semantics",
		1 : "Version 1.1 semantics",
		2 : "ISO 10646 1993 semantics - deprecated",
		3 : "Unicode 2.0 or later semantics - BMP only",
		4 : "Unicode 2.0 or later semantics - non-BMP characters allowed",
		5 : "Unicode Variation Sequences",
		6 : "Full Unicode coverage - used with type 13.0 cmaps by OpenType"
	},
	3 : {
		0 : "Symbol",
		1 : "Unicode BMP-only - UCS-2",
		2 : "Shift-JIS",
		3 : "PRC",
		4 : "BigFive",
		5 : "Johab",
		10 : "Unicode UCS-4"
	}
}

def parseTTF(filePath, options=None):

	with open(filePath, "rb") as file:
				
		file.seek(0)

		# verify that the sfnt version is 1.0
		# note that OpenType fonts are Big Endian!
		tableDirectory = struct.unpack(">IHHHH", file.read(12))
		if tableDirectory[0] != 65536:
			print "Could not verify sfnt version; are you sure this is a TTF file? OTF should be OK, though"
	
		# get number of sub table entries	
		numTables = tableDirectory[1];
		print "Number of tables:",numTables		

		# parse sub table entries
		tableEntries = collections.OrderedDict();
		for i in range(numTables):
			tableEntry = struct.unpack(">BBBBIII", file.read(16))
			tableTag = chr(tableEntry[0]) + chr(tableEntry[1]) + chr(tableEntry[2]) + chr(tableEntry[3])
			tableEntries[tableTag] = {
				"tag": tableTag,
				"checkSum": tableEntry[4],
				"offset": tableEntry[5],
				"length": tableEntry[6]
			}

		# print cmap data
		if options and options[0] == "cmap":
			entry = tableEntries["cmap"]
			if entry == None:
				print "No cmap table!!"
				return

			# print metadata
			print "table: cmap"
			print "\t" + "Checksum:", entry["checkSum"]
			print "\t" + "Offset:",entry["offset"]
			print "\t" + "Length:",entry["length"]

			# seek to cmap table
			file.seek(entry["offset"])

			# get cmap table descriptor			
			tableDesc = struct.unpack(">HH", file.read(4))

			# verify that the cmap table version is 0
			if tableDesc[0] != 0:
				print "Cmap table is not version 0!"
				return
			# verify there is at least 1 encoding table
			if tableDesc[1] <= 0:
				print "Cmap does not contain any encoding tables!"
				return

			print "\tNumber of encoding tables:", tableDesc[1]

			# print cmap encoding table metadata
			for i in range(tableDesc[1]):
				encTable = struct.unpack(">HHI", file.read(8))
				platformId = encTable[0]
				platformSpecificId = encTable[1]

				# make sure platform ID is valid
				if platformId not in [0, 1, 2, 3]:
					print "Invalid platform ID in cmap table entry:", platformId
					return

				print "Encoding Table", i+1
				print "\tPlatform ID:", platformId, "(", ENC_TABLE_PLATFORM[platformId], ")"
				if platformId in [0, 3]:
					print "\tPlatform Specific ID:", platformSpecificId, "(", ENC_TABLE_PLAT_SPECIFIC_ID[platformId][platformSpecificId],")"
 				print "\tOffset:", encTable[2]

		# TODO: handle tables other than cmap?
		elif options:
			print "Currently not supporting table", options[0]
		
		# default to just printing out all table entries
		else:
			for k in tableEntries:
				print "table: " + k
				print "\t" + "Checksum:", tableEntries[k]["checkSum"]
				print "\t" + "Offset:",tableEntries[k]["offset"]
				print "\t" + "Length:",tableEntries[k]["length"]


if __name__ == "__main__":
	numArgs = len(sys.argv)
	if numArgs == 2:
		parseTTF(sys.argv[1]);
	elif numArgs == 3:
		parseTTF(sys.argv[1], [sys.argv[2]])
	else:
		print "Usage:", sys.argv[0], "TTF_input_file [font_table_to_print]"
