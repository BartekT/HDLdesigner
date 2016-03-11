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

def tree_expand(sub_tree, tree):
    remove_list = []

    if type(sub_tree) is dict:
	for k,v in sub_tree.iteritems():
	    st, rl = tree_expand(v, tree)
	    sub_tree[k] = st
	    remove_list += rl
    else:
	for v in sub_tree:
	    if re.match('[0-9a-f]{32}', v):
		pprint(sub_tree)
		pprint(dict(sub_tree))
		sub_tree.remove(v)
		app_tree = tree_key_search(tree, v)
		pprint(app_tree[v])
		pprint(sub_tree)
		sub_tree += app_tree[v]
		remove_list.append(v)
    return sub_tree, remove_list

def parse_to_tree(lst):
    main_tree = {}
    for l in lst:
	for key, val in l.iteritems():
	    tree = {}
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

def parse_level(code):
    blocks = []
    x_hash = hashlib.md5()
    while re.search(r'.*\s(if|case).*?(then|is).*?\send\s(if|case)', code) is not None:
	for x in re.findall(r'.*\s(if|case)(.*?)(then|is)(.*?)(\send\s)(if|case)', code):
	    x_hash.update(''.join(x))
	    code = code.replace(''.join(x), x_hash.hexdigest())
	    blocks.append({x_hash.hexdigest() : ''.join(x)})
    return blocks

def parse_process(code):
    proc = []
    for process in re.findall('.*begin(.*)end.*', code):
	proc.append(parse_to_tree(parse_level(process)))
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

    process_list = []
    for process in re.findall('process\s*\((.*?)\)(.*?)process;', parse_code):
	process_list += parse_process(process[1])
    pprint(process_list)
    signal_assign = []
    for signal in re.findall('\s(.*?)\s*<= .*?;', parse_code):
	signal_assign.append(signal)
    for register in tree_key_search(process_list, '(.*?\'event|rising_edge\(.*?\)|falling_edge\(.*?\))'):
	print register
    fsms = {}
    for fsm,assign in re.findall('([a-zA-Z0-9_]+)\s*<=\s*(.*?);', parse_code):
	if fsm not in fsms:
	    fsms[fsm] = []
#	if assign not in fsms[fsm]:
#	    fsms[fsm].append(asynch)
    return jsonify(process_list = process_list, fsms = fsms)

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
