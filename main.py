from sys import argv, exit
from getopt import getopt, GetoptError

import data_maps

def errorCorrect(info):

	groups = [[], []]

	block_map = data_maps.blockMap()

	byte_array = list(info["byte_array"])

	blocks_in_group_1 = block_map["%s-%s" % (info["version"], info["error_correction_level"])][2]
	blocks_in_group_2 = block_map["%s-%s" % (info["version"], info["error_correction_level"])][4]

	for i in range(blocks_in_group_1):
		groups[0].append([])
	for i in range(blocks_in_group_2):
		groups[1].append([])

	codewords_in_group_1_block = block_map["%s-%s" % (info["version"], info["error_correction_level"])][3]
	codewords_in_group_2_block = block_map["%s-%s" % (info["version"], info["error_correction_level"])][5]

	for block in groups[0]:
		for i in range(codewords_in_group_1_block):
			block.append(byte_array[0])
			del(byte_array[0])


	for block in groups[1]:
		for i in range(codewords_in_group_2_block):
			block.append(byte_array[0])
			del(byte_array[0])

	for byte in info["byte_array"]:
		print int(byte, 2)

def splitIntoBytes(string_of_bytes):

	return [string_of_bytes[start:start + 8] for start in range(0, len(string_of_bytes), 8)]

def breakUpAndPad(info):

	block_map = data_maps.blockMap()

	required_bits = block_map["%s-%s" % (info["version"], info["error_correction_level"])][0] * 8

	byte_string = info["mode_indicator"] + info["character_count_indicator"]

	for byte in info["encoded_text"]:
		byte_string += byte

	terminator = ""

	for i in range(required_bits - len(byte_string)):
		if i > 3:
			break
		terminator += "0"

	byte_string += terminator

	info["terminator"] = terminator
	info["required_bits"] = required_bits

	while len(byte_string) % 8 != 0:
		byte_string += "0"

	pad_byte_strings = ["11101100", "00010001"]
	pad_bytes = []

	for i in range((required_bits - len(byte_string)) / 8):
		byte_string += pad_byte_strings[(i + 2) % 2]
		pad_bytes.append(pad_byte_strings[(i + 2) % 2])

	info["pad_bytes"] = pad_bytes
	info["byte_string"] = byte_string
	info["byte_array"] = splitIntoBytes(byte_string)

	errorCorrect(info)

def encodeAlphanumeric(info):

	alphanumeric_map = data_maps.alphanumericMap()

	encoded_text = []

	character_pairs = []
	character_pairs.append([info["text"][:1]])

	for character in info["text"][1:]:
		if len(character_pairs[-1]) == 1:
			character_pairs[-1].append(character)
		else:
			character_pairs.append([character])

	for pair in character_pairs:
		for character in pair:
			pair[pair.index(character)] = alphanumeric_map[character]

	for pair in character_pairs:
		if len(pair) == 2:
			pair_sum = pair[0] * 45 + pair[1]
			pair_binary = bin(pair_sum)[2:].rjust(11, "0")
			encoded_text.append(pair_binary)
		else:
			pair_binary = bin(pair[0])[2:].rjust(6, "0")
			encoded_text.append(pair_binary)

	info["encoded_text"] = encoded_text

	breakUpAndPad(info)

def addIndicators(info):

	mode_indicators = {"0": "0001", "1": "0010", "2": "0100", "3": "1000"}
	mode_indicator = mode_indicators[str(info["encoding_mode"])]
	info["mode_indicator"] = mode_indicator

	if info["version"] >= 1 and info["version"] <= 9:
		if info["encoding_mode"] == 0:
			character_count_indicator_length = 10
		elif info["encoding_mode"] == 1:
			character_count_indicator_length = 9
		elif info["encoding_mode"] == 2:
			character_count_indicator_length = 8
		else:
			character_count_indicator_length = 8

	elif info["version"] >= 10 and info["version"] <= 26:
		if info["encoding_mode"] == 0:
			character_count_indicator_length = 12
		elif info["encoding_mode"] == 1:
			character_count_indicator_length = 11
		elif info["encoding_mode"] == 2:
			character_count_indicator_length = 16
		else:
			character_count_indicator_length = 10

	elif info["version"] >= 27 and info["version"] <= 40:
		if info["encoding_mode"] == 0:
			character_count_indicator_length = 14
		elif info["encoding_mode"] == 1:
			character_count_indicator_length = 13
		elif info["encoding_mode"] == 2:
			character_count_indicator_length = 16
		else:
			character_count_indicator_length = 12

	character_count_indicator = bin(len(info["text"]))[2:].rjust(character_count_indicator_length, "0")

	info["character_count_indicator"] = character_count_indicator

	if info["encoding_mode"] == 0:
		encodeNumeric(info)
	elif info["encoding_mode"] == 1:
		encodeAlphanumeric(info)
	elif info["encoding_mode"] == 2:
		encodeByte(info)
	else:
		encodeKanji(info)

def determineSmallestVersionForData(info):

	character_capacities = data_maps.characterCapacities()
	list_of_character_counts = []

	for version in character_capacities:
		if character_capacities[version][info["error_correction_level"]][info["encoding_mode"]] >= len(info["text"]):
			list_of_character_counts.append((character_capacities[version][info["error_correction_level"]][info["encoding_mode"]], int(version)))

	info["version"] = int(sorted(list_of_character_counts, key=lambda x: x[1])[0][1])

	addIndicators(info)

def error(error_message, error_code):

	print error_message
	exit(error_code)

def usage():

	error("This is not how you use this util", 2)

def main(argv):

	error_correction_level = False
	encoding_mode_name = False
	text = False

	try:
		opts, args = getopt(argv, "e:m:t:", ["error=", "mode=", "text="])
		for opt in opts:
			if opt[0] == "-e":
				error_correction_level = opt[1]
			elif opt[0] == "-m":
				encoding_mode_name = opt[1]
			elif opt[0] == "-t":
				text = opt[1]

		#To Do: better checking for correct args

		if error_correction_level and encoding_mode_name and text:

			encoding_modes = {
				"numeric": 0,
				"alphanumeric": 1,
				"byte": 2,
				"kanji": 3
			}

			encoding_mode = encoding_modes[encoding_mode_name]

			info = {
				"error_correction_level": error_correction_level,
				"encoding_mode": encoding_mode,
				"text": text,
				"encoding_mode_name": encoding_mode_name
			}

			determineSmallestVersionForData(info)

		else:
			usage()

	except GetoptError:
		usage()

if __name__ == "__main__":
	main(argv[1:])

"""0YOD1QR8HVWHRSDLD2EX6CSCIXHDSDXUHHAAXCVPL599UQFEGB4V252Y8CHHHFKLYXI3M0WM3USBJE4U1234567"""
