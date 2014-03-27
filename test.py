#!/usr/bin/env python

from linker import *
import json
import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

_pillar_ = {
    'logdir': '/var/log/myapp',
    'tomcat': {
        'port': 8080
    },
    'apache': {
        'modjk': {
            'ajp': '__PILLAR_LINK__ tomcat:port',
            'abc': {
                'def': '__PILLAR_LINK__ logdir'
            },
            '123': {
                'another_key': '__PILLAR_LINK__ apache:modjk:abc:def'
            }
        }
    },
    'mysql.port': '__PILLAR_LINK__ db:port'
}

if __name__ == '__main__':
    graph = Graph(flag='__PILLAR_LINK__')
    graph.create(_pillar_)
    graph.topsort()
    print '--------------'
    print '--- PILLAR ---'
    print '--------------'
    print json.dumps(_pillar_, indent=4, sort_keys=True)
    print '--------------------'
    print '--- Sorted Graph ---'
    print '--------------------'
    print graph.sorted
    print '--------------'
    print '--- Result ---'
    print '--------------'
    print json.dumps(
        salt.utils.dictupdate.update(_pillar_, ext_pillar(None, _pillar_)),
        indent=4, sort_keys=True
    )


