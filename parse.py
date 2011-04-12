#!/usr/bin/env python

import re
move_regex = re.compile("[0-9]+\.")
game_result_regex = re.compile("[0-9]+-[0-9]+")

class PGNGame(object):
	def __init__(self):
		self.metas = {}
		self.move_parsers = []
	def __repr__(self):
		return self.__str__()
	def __str__(self):
		s = "<pgngame "
		for k, v in self.metas.iteritems():
			s += str(k) + '="' + str(v) + '" '
		if len(self.move_parsers) > 0:
			s += ">\n"
			for move_parser in self.move_parsers:
				s += str(move_parser)+"\n"
			s += "</pgngame>"
		else:
			s += "/>"
		return s

class BasePGNMoveParser(object):
	def __init__(self, tokens):
		self.tokens = tokens

	def parse_moves(self, context):
		raise Exception("OVERRIDE")

	def __repr__(self):
		return self.__str__()
	def __str__(self):
		s = "<pgnmoveparser "
		s += 'tokens="'+" ".join(self.tokens)+'" '
		s += '/>'
		return s

class PGNGameParser(object):
	def __init__(self, tokens, move_parser_class):
		self.tokens = tokens
		self.move_parser_class = move_parser_class

	def parse_game(self):
		game = PGNGame()
		token_iter = iter(self.tokens)
		while True:
			try:
				token = token_iter.next()
				if token == "[":
					token_iter, meta_tokens = until(token_iter, "]")
					assert len(meta_tokens) >= 3
					assert meta_tokens[1] == '"'
					assert meta_tokens[-1] == '"'
					key = meta_tokens[0]
					value = " ".join(meta_tokens[2:-1])
					game.metas[key] = value
				elif is_move_start(token):
					token_iter, move_tokens = before_next_predicated(token_iter, is_move_start)
					move_parser = self.move_parser_class([token] + move_tokens)
					game.move_parsers.append(move_parser)
				else:
					print "NOT MATCHED: "+token
			except StopIteration:
				break
		return game
	game = property(parse_game)

def is_move_start(token):
	return None != move_regex.match(token)
def is_game_result(token):
    return "*" == token or None != game_result_regex.match(token)

def before_next_predicated(token_iter, predicate):
	sub_tokens = []
	try:
		t = token_iter.next()
		while not predicate(t):
			sub_tokens.append(t)
			t = token_iter.next()
		return push_back(t, token_iter), sub_tokens
	except StopIteration:
		return token_iter, sub_tokens

def push_back(t, token_iter):
	yield t
	for s in token_iter: yield s

def tokenize(chars):
	char_iter = iter(chars)
	current = ""
	in_quote = False
	while True:
		try:
			c = char_iter.next()
			if c in " \t\n":
				if len(current) > 0: yield current
				current = "" 
			elif c in "[]{}()":
				if len(current) > 0: yield current
				current = "" 
				yield c
			elif c == '"':
				yield '"'
				in_quote = True
				d = char_iter.next()
				while d != '"':
					current += d
					d = char_iter.next()
				in_quote = False
				if len(current) > 0: yield current
				current = ""
				yield '"'
			else:
				current += c
		except StopIteration: 
			if in_quote:
				raise Exception("No end quote")
			if len(current) > 0: yield current
			return

def split_games(chars):
	match = "[Event"
	partial_game_chars = str(chars).split(match)
	for chars in partial_game_chars:
		if len(chars) > 0 and not are_whitespace(chars):
			yield match + chars

def are_whitespace(chars):
	for c in chars:
		if c not in " \n\t": return False
	return True 

def until(token_iter, end_token):
	sub_tokens = []
	t = token_iter.next()
	while t != end_token:
		sub_tokens.append(t)
		t = token_iter.next()
	return token_iter, sub_tokens

if __name__ == "__main__":
	import sys
	filename = sys.argv[1]
	with open(filename, 'r') as f:
		chars = f.read()
	game_chars = split_games(chars)
	for chars in game_chars:
		tokens = tokenize(chars)
		game_parser = PGNGameParser(tokens, BasePGNMoveParser)
		game = game_parser.game
		print game

