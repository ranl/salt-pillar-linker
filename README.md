salt-pillar-linker
==================
This external pillar module will provide a way to cross reference pillar data inside pillar it-self.

### salt master config file
```yaml
...
...
ext_pillar:
  - linker: __PILLAR_LINK__
..
..
```
when the pillar linker will encounter a value of a dict that starts with the `__PILLAR_LINK__` string
it will expect the following pattern `__PILLAR_LINK__ address:of:data`
so this mean you will want to point it to `pillar['address']['of']['data']`
you can of course change `__PILLAR_LINK__` to anything you'd like in the salt-master config

### Pillar sls file
```yaml
logdir: /var/log/myapp

tomcat:
  port: 8080

apache:
  modjk:
    ajp: __PILLAR_LINK__ tomcat:port
    abc:
      def: __PILLAR_LINK__ logdir
    123:
      another_key: __PILLAR_LINK__ apache:modjk:abc:def

mysql.port: __PILLAR_LINK__ db:port
```

### Resulting Data
```yaml
logdir: /var/log/myapp

tomcat:
  port: 8080

apache:
  modjk:
    ajp: 8080
    abc:
      def: /var/log/myapp
    123:
      another_key: /var/log/myapp

mysql.port: __PILLAR_LINK__ db:port
```
notice that the value of `mysql.port` didn't change because `pillar['db']['port']` does not exists !

issues
======
* circular links are not supported (since there is no real solution to fix it ... ?)
for example the following will break the pillar linker
```yaml
tomcat:
  port: __PILLAR_LINK__ apache:modjk:ajp
apache:
  modjk:
    ajp: __PILLAR_LINK__ tomcat:port
```
if the pillar linker will encounter this kind of configuration it will log an error to the salt-master and exit !

* referencing from/to indexes in a list is not supported, it might work but I haven't tried it (probably won't work =/)
pull requests are more than welcome =)

external_pillars
================
https://salt.readthedocs.org/en/latest/topics/development/external_pillars.html