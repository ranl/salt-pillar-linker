# coding=utf-8
'''
Add support for referencing items inside pillar it-self

 Notes
-------
- In case of circular linking an exception will be thrown
- Nested links are supported as long as they are not circular

----------------------
       Example
----------------------

 Master Config
---------------
ext_pillar:
  - linker: __PILLAR_LINK__

 Pillar
--------
tomcat:
  port: 8080
apache:
  modjk:
    ajp: __PILLAR_LINK__ tomcat:port

 Output
--------
tomcat:
  port: 8080
apache:
  modjk:
    ajp: 8080
'''

# Python Libs
import logging
import re
from collections import defaultdict

# Salt Libs
import salt.utils.dictupdate
from salt.exceptions import SaltMasterError

# Globals
log = logging.getLogger(__name__)


class Graph():

    def __init__(self, flag='__PILLAR_LINK__'):
        self.flag = flag
        self.re = re.compile(self.flag)
        self.data = defaultdict(set)
        self.sorted = []

    def _append_to_root(self, root, address):
        if not root:
            root = address
        else:
            root += ':{0}'.format(address)
        return root

    def _visit(self, node, marked_nodes, root):
        if marked_nodes[node] == 1:
            msg = 'found a loop node={0} dfs_root={1}'.format(
                node, root
            )
            log.error(msg)
            raise SaltMasterError(msg)
        if marked_nodes[node] == 2:
            return
        marked_nodes[node] = 1
        if node in self.data:
            for child in self.data[node]:
                self._visit(child, marked_nodes, node)
            self.sorted.insert(0, node)
        marked_nodes[node] = 2

    def add_edge(self, src, dst):
        src = src.strip()
        dst = dst.strip()
        self.data[src].add(dst)

    def create(self, pillar, root=''):
        if root == '':
            self.data = defaultdict(set)

        for key, value in pillar.items():
            if isinstance(value, str) and value.startswith(self.flag):
                self.add_edge(
                    self._append_to_root(root, key), self.re.sub('', value)
                )
            elif isinstance(pillar[key], dict):
                self.create(
                    pillar[key], self._append_to_root(root, key)
                )

    def topsort(self):
        self.sorted = []
        marked_nodes = defaultdict(int)
        for node in self.data.keys():
            if marked_nodes[node] == 0:
                self._visit(node, marked_nodes, None)

    def get_neighbors(self, node):
        return self.data[node]


def __virtual__():
    '''
    Always Load
    '''
    return 'linker'


def ext_pillar(minion_id, pillar, command='__PILLAR_LINK__'):
    '''
    Populate pillar data
    '''

    graph = Graph(flag=command)
    graph.create(pillar)
    graph.topsort()
    return linker(pillar, graph)


def linker(pillar, graph):
    '''
    Linker recursive function
    '''

    ret = {}
    for key in graph.sorted:
        for ptr in graph.get_neighbors(key):
            data = salt.utils.traverse_dict(pillar, ptr, '_|-')
            if data == '_|-':
                log.error('missing address "{0}" --> "{1}" in pillar data'.format(key, ptr))
                continue

            update_dict = {}
            keys_to_add = key.split(':')
            final_key = keys_to_add.pop()
            current_location = update_dict
            for k in keys_to_add:
                current_location.update({k: {}})
                current_location = current_location[k]
            current_location[final_key] = data
            salt.utils.dictupdate.update(ret, update_dict)

    return ret
