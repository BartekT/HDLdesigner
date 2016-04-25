#!/usr/bin/python

from flask import Flask, request, jsonify
from flask.ext.cors import CORS
#import MySQLdb
import json
import re
import hashlib
import pydot
from pprint import *

#-------------------------------
# VHDL Parsing functions
#-------------------------------

def tree_key_search(tree, l):
    matched = {}
    if type(tree) is dict:
	for k,v in tree.items():
	    matched.update(tree_key_search(v, l))
	    if re.search(l, k, re.I):
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
	    elif re.search(l, v, re.I):
		matched.append(v)
    if type(tree) is list:
	for v in tree:
	    if type(v) is dict or type(v) is list:
		matched += tree_value_search(v, l)
	    elif re.search(l, v, re.I):
		matched.append(v)
    return matched

def tree_expand(sub_tree, tree):
    if type(sub_tree) is dict:
	for k,v in sub_tree.iteritems():
	    st = tree_expand(v, tree)
	    sub_tree[k] = st
    else:
	for i,v in enumerate(sub_tree):
	    if re.match('[0-9a-f]{32}', v):
		sub_tree.pop(i)
		app_tree = tree_expand(tree_key_search(tree, v), tree)
		sub_tree.insert(i, app_tree[v])
    return sub_tree

def parse_entry(entry):
    tree = {}
    for signal, content in re.findall(r'\s*case\s*(.*?)\s*is\s*(.*)\s*end\scase', entry, re.I):
	sub_tree = {}
	for k,v in re.findall(r'\s*when\s*(.*?)\s*=>\s*(.*?)\s*(?=when|$)', content, re.I):
	    sub_tree.update({k : filter(None,re.split(r'(.*?);\s*', v))})
	tree.update({signal : sub_tree})
    # Parse ifs
    for condition, content in re.findall(r'\s*if\s*(.*?)\s*then\s*.*?(.*?)(?=end\s|els)', entry, re.I):
	tree.update({condition : filter(None,re.split(r'(.*?);\s*', content))})
    # Parse else end if
    for content in re.findall(r'\s*else\s*.*?(.*?)\s*end if', entry, re.I):
	tree.update({"else" : filter(None,re.split(r'(.*?);\s*', content))})
    return tree

def parse_level(code, i):
    blocks = {}
    x_hash = hashlib.md5()
    end = 0
    code_line = code[i]
    i += 1
    while i < len(code):
	if re.search('(^if|^case)', code[i], re.I):
	    if end == 0:
		(sub_block, sub_code_line, curr_i) = parse_level(code, i)
		x_hash.update(sub_code_line)
		blocks.update({x_hash.hexdigest() : parse_entry(sub_code_line)})
		if sub_block:
		    blocks.update(sub_block)
		code_line += x_hash.hexdigest() + ';'
		i = curr_i
		if i >= len(code):
		    return blocks, code_line, i
	    else:
		code_line += ' ' + code[i]
		return blocks, code_line, i
	if code[i].lower() == 'end':
	    end = 1
	code_line += ' ' + code[i]
	i = i + 1
    return blocks, code_line, i

def parse_process(code):
    proc = {}
    for process in re.findall('.*begin\s*(.*)\s*end.*', code, re.I):
	(k, l, m) = parse_level(re.findall(r'\s*(.+?;?)(?=\s|\(|$)', process, re.I), 0)
	proc.update(tree_expand(parse_entry(l), k))
    return proc

def tree_value_grep(tree, val):
    if type(tree) is dict:
	new_tree = {}
	for k,v in tree.iteritems():
	    grep = tree_value_grep(v, val)
	    if grep:
		new_tree[k] = grep
	return new_tree
    elif type(tree) is list:
	new_tree = []
	for v in tree:
	    grep = tree_value_grep(v, val)
	    if grep:
		new_tree.append(grep)
	return new_tree
    else:
	if re.match(val, tree):
	    return tree
    return None

#-------------------------------
# To static file server
#-------------------------------
app = Flask(__name__, static_url_path='')

CORS(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

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

def make_edges(tree, nodes, graph, state, label = None):
    for v in tree:
	if type(v) is dict:
	    for k,l in v.iteritems():
		make_edges(l, nodes, graph, state, k)
	else:
	    for s,val in re.findall('(.*)\s*<=\s*(.*)', v, re.I):
		if val in nodes:
		    if label:
			graph.add_edge(pydot.Edge(nodes[state], nodes[val], label=re.escape(label)))
		    else:
			graph.add_edge(pydot.Edge(nodes[state], nodes[val]))

def paint_fsm(tree, name):
    nodes = {}
    graph = pydot.Dot(graph_type = 'digraph', format = 'svg', graph_name = name)
    for state, assigns in tree.iteritems():
        nodes[state] = pydot.Node(state)
        graph.add_node(nodes[state])
    for state, assigns in tree.iteritems():
        make_edges(assigns, nodes, graph, state)
    return graph.create_svg()

def make_leaf(tree, nodes, graph, link_node):
    if type(tree) is dict:
	for state, assigns in tree.iteritems():
	    graph.add_edge(pydot.Edge(nodes[link_node], nodes[state]))
	    make_leaf(assigns, nodes, graph, state)
    elif type(tree) is list:
	for v in tree:
	    make_leaf(v, nodes, graph, link_node)
    else:
        graph.add_edge(pydot.Edge(nodes[link_node], nodes[tree]))



def paint_output(tree, name):
    nodes = {}
    graph = pydot.Dot(graph_type = 'digraph', format = 'svg', graph_name = name, rankdir='LR')
    for end in list(set(tree_value_search(tree, '.*<=.*'))):
	nodes[end] = pydot.Node(re.escape(end))
	graph.add_node(nodes[end])
    for mid in list(set(tree_key_search(tree, '.*'))):
	nodes[mid] = pydot.Node(re.escape(mid))
	graph.add_node(nodes[end])
    for state, assigns in tree.iteritems():
        nodes[state] = pydot.Node(state)
        graph.add_node(nodes[state])
	make_leaf(assigns, nodes, graph, state)
    return graph.create_svg()


@app.route('/_parse_code', methods = ['POST'])
def parse_code():
    data = json.loads(request.data.decode('utf-8','ignore'))
    # remove comments
    parse_code = re.sub(r'--.*?\n', '', data["data"]);
    # remove special chars
    parse_code = re.sub(r'\s+', ' ', parse_code);

    process_list = {}
    for sensitive, body, name in re.findall('process\s*\((.*?)\)\s*(.*?)\s*process\s*(.*?);', parse_code, re.I):
	process_list.update(parse_process(body))
    signal_assign = []
    for signal in re.findall('\s(.*?)\s*<= .*?;', parse_code, re.I):
	signal_assign.append(signal)
    registers = []
    for k,v in tree_key_search(process_list, '(.*?\'event|rising_edge\s*\(.*?\)|falling_edge\s*\(.*?\))').iteritems():
	for r in tree_value_search(v, '.*<=.*'):
	    if re.findall('(.*?)\s*<=.*', r, re.I) not in registers:
		registers.extend(re.findall('(.*?)\s*<=.*', r, re.I))
    fsms = {}
    for reg in registers:
	reg_tree = tree_key_search(process_list, reg)
	if reg_tree and reg in tree_key_search(process_list, '^' + reg + '$'):
	    output_tree = tree_key_search(process_list, '^' + reg + '$')[reg]
	    try:
		fsms.update({ reg : {
		    "tree" : output_tree,
		    "state_sig" : list(set(re.findall("(.*?)\s*<=.*?;", ";".join(tree_value_search(tree_key_search(process_list, '^' + reg + '$'), '.*?\s*<=.*')), re.I))),
		    "svg" : paint_fsm(output_tree, reg)
		    }})
	    except:
		# Exception handling
		parsing_error = 1
		return jsonify(fsms = {}, outputs = {}, parsing_error = 1)
    outputs = {}
    for output in list(set(re.findall("(.*?)\s*<=.*?;", ";".join(tree_value_search(process_list, '.*?\s*<=.*')), re.I))):
	outputs[output] = paint_output(tree_value_grep(process_list, output), output)
    return jsonify(fsms = fsms, outputs = outputs, parsing_error = 0)

@app.route('/_translate', methods = ['POST'])
def translate():
    data = json.loads(request.data.decode())
    signals = {}
    # remove
    trans_code = re.sub(r'library\s.*?;', '', data["data"], re.I);
    trans_code = re.sub(r'use\s*.*?;', '', trans_code, re.I | re.M);
    # change
    trans_code = re.sub(r'--', '//', trans_code);
    # entity
    for n,s in re.findall('entity\s+(.*?)\s*is\s*(.*?)end.*?;', trans_code, re.I | re.S):
	# scan for signals on entity
	signals_long = []
	signals_short = []
	for v,d,s in re.findall('\s*([a-z0-9_\-,\s]+):\s*(in|out)\sstd_logic(?:_vector\(\s*(.*?)\s*\)|\s*;|\s*\))', s, re.I | re.S):
	    if s:
		signals_long.append(d + 'put [' + re.sub("\sdownto\s", ":", s, re.I) + '] ' +  v + ';')
	    else:
		signals_long.append(d + 'put ' + v + ';')
	    if signals_short:
		signals_short = signals_short + ',' + v
	    else:
		signals_short = v
	trans_code = re.sub('entity\s'+ n +'.*?end ' + n + ';', 'module ' + n + '(' + signals_short + ');\n' + '\n'.join(signals_long), trans_code, flags = re.I | re.S);
	# architecture
	for arch_name in re.findall('architecture\s+(.*?)\s+of\s+' + n + '\s+is', trans_code, re.I | re.S):
	    for header, content in re.findall('architecture\s+' + arch_name + '\s+of\s+' + n + '\s+is(.*?)begin(.*?)end\s+' + arch_name + ';', trans_code, re.I | re.S):
		print header, content

    return jsonify(trans_code = trans_code)

if __name__ == '__main__':

#    conn = MySQLdb.connect (host = "localhost",
#	    user = "proc",
#	    passwd = "proc123",
#	    db = "proc")
#    cursor = conn.cursor()

    app.run(
        host="0.0.0.0",
        port=int("5000"),
        debug=True
    )

#    conn.close()
