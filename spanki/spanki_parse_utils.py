#!/usr/bin/env python
# encoding: utf-8

import re
import sys
import argparse
import pysam
import collections
import math


def parseRefAsBam(samfile):
	EDG = {}
	JUN = {}
	for alignedread in samfile:
		if (len(alignedread.cigar) > 1):
			strand = alignedread.tags[0][1] 
			mytid = alignedread.tid
			txid = str(alignedread.qname)
			chr = samfile.getrname(mytid)
			start = alignedread.pos
			offset = start
			gaps = []
			matches = []
			addnextmatch = 0
			addtomatch = 0
			for i in alignedread.cigar:
				# Iterate over each entry in cigar
				# matches should be appended 
				if (i[0] == 0):
					if addnextmatch > 0:
						matches[-1] = matches[-1] + i[1] + addtomatch
						addnextmatch = 0
						addtomatch = 0
					else: matches.append(i[1])
				elif (i[0] == 3):
					gaps.append(i[1])
				elif (i[0] == 1):
					addnextmatch += 1
					addtomatch = 0
				elif (i[0] == 2):
					addnextmatch += 1
					addtomatch = i[1]
									
			if len(gaps) > 0:
				for i in range(len(gaps)):
					junc_left_side = start + matches[i] + 1
					junc_right_side = start + matches[i] + gaps[i] 
					juncid = chr + ":" + str(junc_left_side) + "_" + str(junc_right_side) + ":" + strand
					if (strand == '+'):
						donid = chr + ":" + str(junc_left_side)
						accid = chr + ":" + str(junc_right_side)
					else:
						donid = chr + ":" + str(junc_right_side)
						accid = chr + ":" + str(junc_left_side)
					EDG[donid] = txid
					EDG[accid] = txid
					JUN[juncid] = 1
					start = start + matches[i] + gaps[i];	
					
 	#samfile.close()
 	refjunclist = JUN.keys()
 	refjunclist.sort()
 	return EDG, refjunclist


def edgeConnections(samfile):
	EDGconnections = collections.defaultdict(list)
	donlist = []
	acclist = []
	for alignedread in samfile:
		if (len(alignedread.cigar) > 1):
			strand = alignedread.tags[0][1] 
			mytid = alignedread.tid
			txid = str(alignedread.qname)
			chr = samfile.getrname(mytid)
			start = alignedread.pos
			offset = start
			gaps = []
			matches = []
			addnextmatch = 0
			addtomatch = 0
			for i in alignedread.cigar:
				# Iterate over each entry in cigar
				# matches should be appended 
				if (i[0] == 0):
					if addnextmatch > 0:
						matches[-1] = matches[-1] + i[1] + addtomatch
						addnextmatch = 0
						addtomatch = 0
					else: matches.append(i[1])
				elif (i[0] == 3):
					gaps.append(i[1])
				elif (i[0] == 1):
					addnextmatch += 1
					addtomatch = 0
				elif (i[0] == 2):
					addnextmatch += 1
					addtomatch = i[1]
									
			if len(gaps) > 0:
				for i in range(len(gaps)):
					junc_left_side = start + matches[i] + 1
					junc_right_side = start + matches[i] + gaps[i] 
					juncid = chr + ":" + str(junc_left_side) + "_" + str(junc_right_side) + ":" + strand
					if (strand == '+'):
						donid = chr + ":" + str(junc_left_side)
						accid = chr + ":" + str(junc_right_side)
					else:
						donid = chr + ":" + str(junc_right_side)
						accid = chr + ":" + str(junc_left_side)
					EDGconnections[donid].append(accid)
					EDGconnections[accid].append(donid)
					donlist.append(donid)
					acclist.append(accid)
					start = start + matches[i] + gaps[i];	
					
 	#samfile.close()
 	donlist = list(set(donlist))
 	acclist = list(set(acclist))
 	return EDGconnections, donlist, acclist

def get_junc_positions(samfile):
	#FBtr0091780	16	chr3R	4029917	255	523M54N59M	*	0	0	*	*	XS:A:-
	TX = collections.defaultdict(lambda : collections.defaultdict(dict))
	#JUNCTIONS = collections.defaultdict(lambda : collections.defaultdict(dict))
	JUNCORDERS = collections.defaultdict(list)
	JUNCSTARTD = collections.defaultdict(list)
	JUNCENDD = collections.defaultdict(list)
	#EDG = {}
	#JUN = {}
	for alignedread in samfile:
		if (len(alignedread.cigar) > 1):
			strand = alignedread.tags[0][1] 
			mytid = alignedread.tid
			txid = str(alignedread.qname)
			chr = samfile.getrname(mytid)
			start = alignedread.pos
			end = alignedread.aend
			
			if strand == "+":
				txstart = start
				txend = end
			elif strand == "-":
				txstart = end
				txend = start
			else:
				quit("Don't recongnize strand")
			
					
			
			numjuncs = len(alignedread.cigar) - 1
			TX[txid]['chr'] = chr
			TX[txid]['start'] = start
			TX[txid]['end'] = end
			TX[txid]['strand'] = strand
			TX[txid]['numjuncs'] = numjuncs
			juncorder = 0
			
			offset = start
			gaps = []
			matches = []
			addnextmatch = 0
			addtomatch = 0
			for i in alignedread.cigar:
				# Iterate over each entry in cigar
				# matches should be appended 
				if (i[0] == 0):
					if addnextmatch > 0:
						matches[-1] = matches[-1] + i[1] + addtomatch
						addnextmatch = 0
						addtomatch = 0
					else: matches.append(i[1])
				elif (i[0] == 3):
					gaps.append(i[1])
				elif (i[0] == 1):
					addnextmatch += 1
					addtomatch = 0
				elif (i[0] == 2):
					addnextmatch += 1
					addtomatch = i[1]
									
			if len(gaps) > 0:
				for i in range(len(gaps)):
					junc_left_side = start + matches[i] + 1
					junc_right_side = start + matches[i] + gaps[i] 
					juncid = chr + ":" + str(junc_left_side) + "_" + str(junc_right_side) + ":" + strand
					if (strand == '+'):
						donid = chr + ":" + str(junc_left_side)
						accid = chr + ":" + str(junc_right_side)
					else:
						donid = chr + ":" + str(junc_right_side)
						accid = chr + ":" + str(junc_left_side)
					juncorder += 1
					
					#JUNCTIONS[juncid]['order'].append(juncorder)
					#print "Juncorder is ", juncorder
					if strand == "+":
						startd = junc_left_side - txstart
						endd = txend - junc_right_side
						##print junc_left_side
						##print txstart
						##print txend
						##print startd
						##print endd
					elif (strand == "-"):
						startd = txstart - junc_right_side
						endd = junc_right_side - txend
					else:
						quit("Don't recongnize strand")
										
					##print "bleh", endd
					JUNCORDERS[juncid].append(juncorder)
					JUNCSTARTD[juncid].append(startd)
					JUNCENDD[juncid].append(endd)
					start = start + matches[i] + gaps[i];	


					
 	#samfile.close()
 	#refjunclist = JUN.keys()
 	#refjunclist.sort()
 	return TX, JUNCORDERS, JUNCSTARTD, JUNCENDD


def parseRefAsBamReturnJuncs(samfile):
	EDG = {}
	#JUN = {}
	JUN = collections.defaultdict(lambda : collections.defaultdict(dict))
	for alignedread in samfile:
		if (len(alignedread.cigar) > 1):
			strand = alignedread.tags[0][1] 
			mytid = alignedread.tid
			txid = str(alignedread.qname)
			chr = samfile.getrname(mytid)
			start = alignedread.pos
			offset = start
			gaps = []
			matches = []
			addnextmatch = 0
			addtomatch = 0
			for i in alignedread.cigar:
				# Iterate over each entry in cigar
				# matches should be appended 
				if (i[0] == 0):
					if addnextmatch > 0:
						matches[-1] = matches[-1] + i[1] + addtomatch
						addnextmatch = 0
						addtomatch = 0
					else: matches.append(i[1])
				elif (i[0] == 3):
					gaps.append(i[1])
				elif (i[0] == 1):
					addnextmatch += 1
					addtomatch = 0
				elif (i[0] == 2):
					addnextmatch += 1
					addtomatch = i[1]
									
			if len(gaps) > 0:
				for i in range(len(gaps)):
					junc_left_side = start + matches[i] + 1
					junc_right_side = start + matches[i] + gaps[i] 
					juncid = chr + ":" + str(junc_left_side) + "_" + str(junc_right_side) + ":" + strand
					if (strand == '+'):
						donid = chr + ":" + str(junc_left_side)
						accid = chr + ":" + str(junc_right_side)
					else:
						donid = chr + ":" + str(junc_right_side)
						accid = chr + ":" + str(junc_left_side)
					EDG[donid] = txid
					EDG[accid] = txid
					if JUN[juncid]:
						JUN[juncid].append(txid)
					else:
						JUN[juncid] = [txid]
					start = start + matches[i] + gaps[i];	
					
 	#samfile.close()
 	refjunclist = JUN.keys()
 	refjunclist.sort()
 	return EDG, refjunclist, JUN

def parseRefSelectionAsBam(samfile,txlist):
	EDG = {}
	JUN = {}
	for alignedread in samfile:
		mytid = alignedread.tid
		txid = str(alignedread.qname)
		if txid in txlist:
			if (len(alignedread.cigar) > 1):
				strand = alignedread.tags[0][1] 
				mytid = alignedread.tid
				txid = str(alignedread.qname)
				chr = samfile.getrname(mytid)
				start = alignedread.pos
				offset = start
				gaps = []
				matches = []
				addnextmatch = 0
				addtomatch = 0
				for i in alignedread.cigar:
					# Iterate over each entry in cigar
					# matches should be appended 
					if (i[0] == 0):
						if addnextmatch > 0:
							matches[-1] = matches[-1] + i[1] + addtomatch
							addnextmatch = 0
							addtomatch = 0
						else: matches.append(i[1])
					elif (i[0] == 3):
						gaps.append(i[1])
					elif (i[0] == 1):
						addnextmatch += 1
						addtomatch = 0
					elif (i[0] == 2):
						addnextmatch += 1
						addtomatch = i[1]
										
				if len(gaps) > 0:
					for i in range(len(gaps)):
						junc_left_side = start + matches[i] + 1
						junc_right_side = start + matches[i] + gaps[i] 
						juncid = chr + ":" + str(junc_left_side) + "_" + str(junc_right_side) + ":" + strand
						if (strand == '+'):
							donid = chr + ":" + str(junc_left_side)
							accid = chr + ":" + str(junc_right_side)
						else:
							donid = chr + ":" + str(junc_right_side)
							accid = chr + ":" + str(junc_left_side)
						EDG[donid] = txid
						EDG[accid] = txid
						JUN[juncid] = 1
						start = start + matches[i] + gaps[i];	
					
 	#samfile.close()
 	refjunclist = JUN.keys()
 	refjunclist.sort()
 	return EDG, refjunclist


if __name__ == "__main__":
    sys.exit(main())
