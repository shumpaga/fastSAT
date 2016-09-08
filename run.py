#! /usr/bin/env python3.5

import argparse
import os
import subprocess
import re
import sys
import threading

BLUE = '\033[94m'
DARKBLUE = '\033[0,34m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
NO = '\033[0m'

class RunCmd(threading.Thread):
    def __init__(self, cmd, timeout):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.timeout = timeout

    def run(self):
        self.p = subprocess.Popen(self.cmd, stdout=subprocess.PIPE,
                universal_newlines=True)
        self.p.wait()

    def Run(self):
        self.start()
        self.join(self.timeout)
        if self.is_alive():
            self.p.terminate() # use self.p.kill() if process needs a kill -9
            self.join()
        else:
            return self.p.communicate()[0]


def safeOpen(file_path, acl):
    try:
        f = open(file_path, acl)
    except Exception as e:
        print(e)
        exit()
    return f

def parseConf(dir_path, fpath):
    conf = safeOpen(dir_path + '/' + str(fpath), 'r')
    cmds = []
    states = []
    for line in conf:
        if line[0] == '#':
            continue
        elif line[0] != 't':
            conf.close()
            print('Usage: t <formula> t', file=sys.stderr)
            exit(0)
        cmds.append(re.search('t (.+?) t', line).group(1))
        states.append(re.search('--> (.+?) s', line).group(1))
    conf.close()
    return cmds, states

def parseBins(dir_path):
    bins = []
    for root, dirs, files in os.walk(dir_path + '/bin'):
        for name in files:
            bins.append(name)
    return bins

def cleanString(string, mode):
    if mode == "name":
        res = ''.join(e for e in string if e.isalpha())
        return re.search('(.+?)bench', res).group(1)
    elif mode == "iteration":
        return ''.join(e for e in string if e.isnumeric())
    else:
        return ''.join(e for e in string if e.isalnum())

def parseTime(template, line):
    words = line.split()
    name = cleanString(words[0], "name")
    time = cleanString(words[1], "") + cleanString(words[2], "")
    cpu = cleanString(words[3], "") + cleanString(words[4], "")
    iteration = cleanString(words[5], "iteration")

    return template.format("{}{}".format(GREEN, name),
            "{}{}".format(YELLOW, time),
            "{}{}".format(YELLOW, cpu),
            "{}{}{}".format(BLUE, iteration, NO))

def parseResult(line):
    words = line.split()
    return words[1] + ' ' + words[2]

def printTable(res, i, template):
# Print functions that have been timeout
    for j in range(len(res[i])):
        if "TIMEOUT" in res[i][j]:
            print(res[i][j])
# Print the rest
    print('{}{:-<80}{}'.format(BLUE, '', NO))
    print(template.format("{}{}".format(GREEN, "Function name"),
        "{}{}".format(YELLOW, "Time"),
        "{}{}".format(YELLOW, "CPU"),
        "{}{}{}".format(BLUE, "Iteration", NO)))
    print('{}{:-<80}{}'.format(BLUE, '', NO))
    for j in range(len(res[i])):
        if "TIMEOUT" in res[i][j]:
            continue
        print(res[i][j])
    print('{}{:-<80}{}'.format(BLUE, '', NO))

def print_result(template, cmds, res1, res2):
# Print title
    for i in range(len(cmds)):
        print('{}{:#<80}{}'.format(BLUE, '', NO))
        print('{}{:#^80}{}'.format(BLUE, '||    {}    ||'.format(cmds[i]), NO))
        print('Complete cycles of minimisation')
        printTable(res1, i, template)
        print('Forced number of states')
        printTable(res2, i, template)
    print()


def getResult(r, j, bins, template):
    tmp = []
    if (r):
        lines = r.splitlines()
        tmp.append(parseTime(template, lines[-1]))
        tmp.append(parseResult(lines[-2]))
    else:
        tmp.append('{}{}{}'.format(RED,
            '{}{}{} --> TIMEOUT'.format(GREEN, bins[j], RED), NO))
    return tmp

def run(fpath, time, save_path):
# Get all cmds in bench.conf file, get binaries names, and initiate res
    dir_path = os.path.dirname(os.path.realpath(__file__))
    cmds, states = parseConf(dir_path, fpath)
    bins = parseBins(dir_path)
    res1 = [] # For the classic test
    res2 = [] # The same test but by forcing the number of states
# Set PATH in order to be able to find the binaries
    cur_path = os.environ["PATH"]
    os.environ["PATH"] = dir_path + '/bin:' + cur_path
# Template for printing
    template = "{0:30}|{1:25}|{2:15}|{3:1}"
# Start execution
    for i in range(len(cmds)):
        res1.append([])
        res2.append([])
        for j in range(len(bins)):
            cmd1 = [dir_path + '/fastSAT', cmds[i], bins[j]]
            cmd2 = [dir_path + '/fastSAT', cmds[i], bins[j], states[i]]
            r1 = RunCmd(cmd1, time).Run()
            r2 = RunCmd(cmd2, time).Run()
            res1[i].extend(getResult(r1, j, bins, template))
            res2[i].extend(getResult(r2, j, bins, template))
# Print result or save into file
    orig_stdout = sys.stdout
    save = None
    if (save_path):
        save = safeOpen(dir_path + '/' + save_path, 'w')
        sys.stdout = save
    print_result(template, cmds, res1, res2)
    sys.stdout = orig_stdout
    if (save):
        save.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str,
            help='path to bench.conf file')
    parser.add_argument('-t', '--timeout', type=int,
            help='timeout for each test (in seconds)')
    parser.add_argument('-s', '--save', type=str,
            help='path to save file')
    args = parser.parse_args()

    if (args.file):
        run(args.file, args.timeout, args.save)
    else:
        run('bench.conf', args.timeout, args.save)

if __name__ == '__main__':
    main()
