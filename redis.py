#! /bin/python3

import os
import sys
import getopt
import sqlite3

OPTION_DICT = {}
CONN = sqlite3.connect("redis.db")
CUR = CONN.cursor()


def show_help():
    print('''
Usage: OBJECT {COMMAND | help} [ OPTIONS ]
where  OBJECT := { help | list | add | test | conn | del}
       OPTIONS := { -n[ame] | -h[ost] | -p[ort] | -a[uth] } 
    ''')


def add(name, host, port, auth):
    CONN.execute("insert into dbs(name, host, port, auth) values(?,?,?,?);", (name, host, port, auth))
    CONN.commit()
    CONN.close()


def list():
    CUR.execute("select name, host, port from dbs")
    res = CUR.fetchall()
    CUR.close()
    CONN.close()
    if len(res) != 0:
        print("name\t\thost\t\tport")
    for line in res:
        print("{}\t\t{}\t\t{}".format(line[0], line[1], line[2]))


def conn(name):
    CUR.execute("select host, port, auth from dbs where name=?;", (name))
    res = CUR.fetchall()
    CUR.close()
    CONN.close()
    if len(res) == 0:
        raise RuntimeError('The specified name can not find.')
    info = res[0]
    _command = 'redis-cli -h {} -p {} -a {}'.format(info[0], info[1], info[2])
    # print(_command)
    os.system(_command)


def delete(name):
    CUR.execute("delete from dbs where name='{}';".format(name))
    CUR.close()
    CONN.close()
    pass


def test(host, port, auth):
    return True


def check_and_exec(_command):
    name = None if '-n' not in OPTION_DICT.keys() else OPTION_DICT['-n']
    host = None if '-h' not in OPTION_DICT.keys() else OPTION_DICT['-h']
    port = None if '-p' not in OPTION_DICT.keys() else OPTION_DICT['-p']
    auth = None if '-a' not in OPTION_DICT.keys() else OPTION_DICT['-a']
    if _command == 'help':
        show_help()
    elif _command == 'list':
        list()
        pass
    elif _command == 'add':
        if host is None:
            raise RuntimeError('The host can not be null when connect.')
        if test(host, port, auth):
            add(name, host, port, auth)
        else:
            print('Connect failed, please check the info and retry.')
        pass
    elif _command == 'test':
        if host is None:
            raise RuntimeError('The host can not be null when connect.')
        if test(host, port, auth) is False:
            print('Connect failed.')
        pass
    elif _command == 'conn':
        if name is None:
            raise RuntimeError('The name can not be null when connect.')
        conn(name)
        pass
    elif _command == 'del':
        if name is None:
            raise RuntimeError('The name can not be null when delete.')
        delete(name)
        pass


if __name__ == '__main__':
    command = sys.argv[1]
    options = sys.argv[2:]
    try:
        opts, args = getopt.getopt(options, "-n:-h:-p:-a:")
        for opt, arg in opts:
            OPTION_DICT[opt] = arg

        check_and_exec(command)
    except (getopt.GetoptError, Exception) as e:
        if e == getopt.GetoptError:
            show_help()
            exit(2)
        else:
            raise e
