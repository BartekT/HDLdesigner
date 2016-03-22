#!/usr/bin/python

from flask import Flask, request, jsonify
import MySQLdb
import json
import re
import hashlib
from pprint import *

#-------------------------------
# VHDL Parsing functions
#-------------------------------

def tree_key_search(tree, l):
    matched = {}
    if type(tree) is dict:
	for k,v in tree.items():
	    matched.update(tree_key_search(v, l))
	    if re.search(l, k):
		matched.update({ k: v })
    if type(tree) is list:
	for v in tree:
	    if type(v) is dict or type(v) is list:
		matched.update(tree_key_search(v, l))
    return matched

def tree_value_search(tree, l):
    matched = []
    if type(tree) is dict:
	for k,v in tree.items():
	    if type(v) is dict or type(v) is list:
		matched += tree_value_search(v, l)
	    elif re.search(l, v):
		matched.append(v)
    if type(tree) is list:
	for v in tree:
	    if type(v) is dict or type(v) is list:
		matched += tree_value_search(v, l)
	    elif re.search(l, v):
		matched.append(v)
    return matched

def tree_expand(sub_tree, tree):
    remove_list = []

    if type(sub_tree) is dict:
	for k,v in sub_tree.iteritems():
	    st, rl = tree_expand(v, tree)
	    sub_tree[k] = st
	    remove_list += rl
    else:
	for i,v in enumerate(sub_tree):
	    if re.match('[0-9a-f]{32}', v):
		sub_tree.pop(i)
		app_tree = tree_key_search(tree, v)
		sub_tree.insert(i, app_tree[v])
		remove_list.append(v)
    return sub_tree, remove_list

def parse_to_tree(lst):
    main_tree = {}
    for l in lst:
	for key, val in l.iteritems():
	    tree = {}
	    if_tree = []
	    # Parse cases
	    for signal, content in re.findall(r'\s*case\s*(.*?)\s*is\s*(.*)end\scase', val):
		sub_tree = {}
		for k,v in re.findall(r'when\s*(.*?)\s*=>\s*(.*?)\s*(?=when|$)', content):
		    sub_tree.update({k : filter(None,re.split(r'(.*?);\s*', v))})
		tree.update({signal : sub_tree})
	    # Parse ifs
	    for condition, content in re.findall(r'\s*if\s*(.*?)\s*then\s*.*?(.*?)(?=end\s|els)', val):
		tree.update({condition : filter(None,re.split(r'(.*?);\s*', content))})
	    # Parse else end if
	    for content in re.findall(r'\s*else\s*.*?(.*?)end if', val):
		tree.update({"else" : filter(None,re.split(r'(.*?);\s*', content))})
	    main_tree.update({ key : tree })
    # Rebuild tree
    mt, rm = tree_expand(main_tree, main_tree)
    for v in rm:
	del mt[v]
    return main_tree

def parse_level(code, i):
    blocks = []
    end = 0
    sub_prog = 0
    code_line = ''
    while i < len(code):
	if re.search('(^if|^case)', code[i]):
	    if len(code_line) > 0:
		blocks.append(code_line)
		code_line = ''
	    if end == 0:
		(sub_block, curr_i) = parse_level(code, i + 1)
		i = curr_i
		blocks.append(sub_block)
		if i >= len(code):
		    return blocks, i
	    else:
		return blocks, i
	if code[i] == 'end':
	    end = 1
	else:
	    code_line += ' ' + code[i]
	i = i + 1
    return blocks, i

def parse_process(code):
    proc = {}
    for process in re.findall('.*begin(.*)end.*', code):
	(k, l) = parse_level(re.findall(r'\s*(.+?;?)(?=\s|\(|$)', process), 0)
	#proc.update(k)
	pprint(k)
    return proc



#-------------------------------
# To static file server
#-------------------------------
app = Flask(__name__, static_url_path='')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/cpu')
def cpu():
    return app.send_static_file('cpu.html')

@app.route('/_load_instr')
def load_instr():
    cursor.execute("SELECT mnemonics.opcode, mnemonics.name, modes_desc.short FROM `mnemonics` LEFT JOIN modes_desc ON mnemonics.mode = modes_desc.id")
    opcode_matrix = [['' for x in range(16)] for y in range(16)]
    opcode_matrix_short = [['' for x in range(16)] for y in range(16)]
    for opcode in cursor.fetchall():
	opcode_matrix[int(opcode[0][0], 16)][int(opcode[0][1], 16)] = opcode[1]
	opcode_matrix_short[int(opcode[0][0], 16)][int(opcode[0][1], 16)] = opcode[2]
    cursor.execute("SELECT * FROM `instructions` ORDER BY opcode, state, 'signal'")
    opcode_cycle = {}
    max_signal_lengths = {}
    max_states = {}
    for opcode in cursor.fetchall():
	if opcode[0] not in opcode_cycle:
	    opcode_cycle[opcode[0]] = {}
	    max_signal_lengths[opcode[0]] = 0;
	    max_states[opcode[0]] = 0;
	if opcode[0] in opcode_cycle and opcode[1] not in opcode_cycle[opcode[0]]:
	    opcode_cycle[opcode[0]][opcode[1]] = []
	opcode_cycle[opcode[0]][opcode[1]].append(opcode[2])
	if max_signal_lengths[opcode[0]] < len(opcode_cycle[opcode[0]][opcode[1]]):
	    max_signal_lengths[opcode[0]] = len(opcode_cycle[opcode[0]][opcode[1]])
	if max_states[opcode[0]] < len(opcode_cycle[opcode[0]]):
	    max_states[opcode[0]] = len(opcode_cycle[opcode[0]])
    return jsonify(opcode_matrix = opcode_matrix
		    , opcode_matrix_short = opcode_matrix_short
		    , opcode_cycle = opcode_cycle
		    , max_signal_lengths = max_signal_lengths
		    , max_states = max_states)

@app.route('/_parse_code', methods = ['POST'])
def parse_code():
    data = json.loads(request.data.decode())
    # remove comments
    parse_code = re.sub(r'--.*?\n', '', data["data"]);
    # remove special chars
    parse_code = re.sub(r'\s+', ' ', parse_code);

    process_list = {}
    for process in re.findall('process\s*\((.*?)\)(.*?)process;', parse_code):
	process_list.update(parse_process(process[1]))
    pprint(process_list)
    signal_assign = []
    for signal in re.findall('\s(.*?)\s*<= .*?;', parse_code):
	signal_assign.append(signal)
    registers = []
    for k,v in tree_key_search(process_list, '(.*?\'event|rising_edge\(.*?\)|falling_edge\(.*?\))').iteritems():
	print k
	registers = re.findall('(.*?)\s*<=.*', ';'.join(tree_value_search(v, '.*<=.*')))
    pprint(registers)
    fsms = {}
    for reg in registers:
	reg_tree = tree_key_search(process_list, reg)
	if reg_tree:
	    fsms.update({ reg : { "tree" : tree_key_search(process_list, reg)[reg],
		"output" : list(set(re.findall("(.*?)\s*<=.*?;", ";".join(tree_value_search(tree_key_search(process_list, reg), '.*?\s*<=.*')))))}})
    pprint(fsms)
    return jsonify(process_list = process_list, fsms = fsms, registers = registers)

if __name__ == '__main__':

    conn = MySQLdb.connect (host = "localhost",
	    user = "proc",
	    passwd = "proc123",
	    db = "proc")
    cursor = conn.cursor()

    app.run(
        host="0.0.0.0",
        port=int("5000"),
        debug=True
    )

    conn.close()
