#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=unused-wildcard-import
'''
This oswalk is used to demonstrate

1) os.walk
2) functor
3) strategy design pattern
4) optparser
5) bisect
6) copy

By wweiradio@sina.com


'''

import os
import optparse
import bisect
import copy


def find_basename(path):
  return os.path.basename(path)

def humanize(size):
    if size <1024:
        return "{0}bytes".format(size)
    elif size <1024*1024:
        return "{0}Kbytes".format(size/1024)
    elif size <1024*1024*1024:
        return "{0}Mbytes".format(size/1024/1024)
    else:
        return "{0}Gbytes".format(size/1024/1024)


class LargeFiles(object):
    def __init__(self, limit=10):
        self.files = []
        self.limit = limit

    def insert(self, filename, size):
        bisect.insort(self.files, (size, filename))
        if len (self.files) > self.limit:
            self.files.pop(0)

    def __str__(self):
        self.files.reverse()
        files = copy.deepcopy(self.files)
        out = ["[{0}]-{1} - {2}".format(num, atuple[1], humanize(atuple[0])) for num, atuple in enumerate(files, start=1)]
        return "\n".join(out)


class WalkBase(object):
    def __init__(self, path):
        self.path = path.rstrip(os.sep)
        self.base_depth = path.count(os.sep)

    def __call__(self, *args, **kwargs):
        self.walk()

    def walk(self):
        for current_dir, dirs_in_current_dir, files_in_current_dir in os.walk(self.path):
            self.internal_process(current_dir, dirs_in_current_dir, files_in_current_dir)
        self.end()
    def end(self):
        pass

    def internal_process(self, current_dir, dirs_in_current_dir, files_in_current_dir):
        raise NotImplemented


class TopWalk(WalkBase):
    def __init__(self, path, limit=None):
        super(TopWalk, self).__init__(path)
        self.limit = limit if limit else 10
        self.largeFile = LargeFiles(self.limit)

    def internal_process(self, current_dir, dirs_in_current_dir, files_in_current_dir):
        for file in files_in_current_dir:
            filepath = os.sep.join([current_dir, file])
            size = os.path.getsize(filepath)
            self.largeFile.insert(filepath, size)
    def end(self):
        print str(self.largeFile)

class ShowWalk(WalkBase):
    def __init__(self, path, showSize=False):
        super(ShowWalk,self).__init__(path)
        self.showsize = showSize

    def internal_process(self, current_dir, dirs_in_current_dir, files_in_current_dir):
        depth = current_dir.count(os.sep) - self.base_depth
        print "  " * depth + find_basename(current_dir) + os.sep
        for file in files_in_current_dir:
            filepath = os.sep.join([current_dir, file])
            size = os.path.getsize(filepath)
            if self.showsize:
                print "{0}{1} - [{2}]".format("  " * (depth + 1), find_basename(file), humanize(size))
            else:
                print "{0}{1}".format("  " * (depth + 1), find_basename(file))


def walk_path(path, top=None, showSize=False):

    if top:
        TopWalk(path, limit=top)()
    else:
        ShowWalk(path, showSize = showSize)()


def main():

    parser = optparse.OptionParser()

    parser.add_option("-t", "--top", dest="top", action="store", type="int",
                      help=("show top10 largest files [deault:%default]"),
                      )
    parser.add_option("-s", "--size",  dest="showsize", default=False,
                      help=("give the sizes in the end of line [deault:%default]"),
                      action="store_true")

    parser.set_defaults(showsize=False, top=-1)

    opts, args = parser.parse_args()

    if not args:
        args =["."]

    if opts.top < 0:
        opts.top = None

    for item in args:
        print "+++" * 10
        walk_path(item, top= opts.top, showSize=opts.showsize)

    print ("Done.")

if __name__ == "__main__":
    main()