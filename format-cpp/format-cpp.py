#!/usr/bin/env python

import os
import re
import sys

# list of extensions to replace
replace_extensions = [".cpp", ".h", ".mm"]
files_to_skip = None

def try_to_replace(fname):
    if replace_extensions:
        for replace_extension in replace_extensions:
            if fname.lower().endswith(replace_extension):
                return True
        return False
    return True


def replacement(m):
    # print "group 2: ", m.group(2)
    name_prefix = m.group(3)
    first = name_prefix[0]
    second = ""
    # if m.group(2) == "m_p" or m.group(2) == "m_s":
    #     if name_prefix[0].islower():
    #         first = m.group(2)[-1]
    #         name_prefix = first + name_prefix

    if len(name_prefix) > 1:
        second = name_prefix[1]

    if first.isupper() and second.islower():
        first = first.lower()
        name_prefix = first + name_prefix[1:]
        return m.group(1) + "_" + name_prefix
    elif first.isupper() and second.isupper():
        return m.group(1) + "_" + name_prefix
    else:
        print "don't convert: ", m.group(1) + m.group(2) + m.group(3)
    if m.group(2) == "m_":
        return m.group(1) + "_" + name_prefix
    return m.group(1) + m.group(2) + m.group(3)

def file_replace(fname, pat):
    # first, see if the pattern is even in the file.
    with open(fname) as f:
        if not any(re.search(pat, line) for line in f):
            # print "can't find the string..."
            return # pattern does not occur in file so we are done.

    # pattern is in the file, so perform replace operation.
    with open(fname) as f:
        out_fname = fname + ".tmp"
        out = open(out_fname, "w")
        for line in f:
            repl = line
            # for match in re.finditer(pat, line):
            #     print match.regs
            #     print match.group(1)
            #
            # matches = re.findall(pat, line)
            # print matches
            m = re.search(pat, line)
            if m:
                # repl = re.sub(pat, "_" + r'\1', line)
                repl = re.sub(pat, replacement, line)

            out.write(repl)
        out.close()
        os.rename(out_fname, fname)


def mass_replace(dir_name, s_before):
    pat = re.compile(s_before)
    for dirpath, dirnames, filenames in os.walk(dir_name):
        for fname in filenames:
            if try_to_replace(fname):
                fullname = os.path.join(dirpath, fname)
                need_skip = False
                if files_to_skip != None:
                    for skip in files_to_skip:
                        if fullname.find(skip) != -1:
                            print "skip file: ", fullname
                            need_skip = True
                            break
                if not need_skip:
                    file_replace(fullname, pat)



prefix_need_replace = [
    "m_pob",
    "m_ob",
    "m_str",
    "m_psz",
    "m_sz",
    "m_pfn",
    "m_pf",
    "m_s",
    "m_p",
    "m_b",
    "m_n",
    "m_h",
    "m_u",
    "m_c",
    "m_e",
    "m_f",
    "m_d",
    "m_t",
    "m_i",
    "m_"
]

def do_replace(dir, dir_skip_list):
    """

    Arguments:
    - `dir`:
    - `dir_skip`:
    """
    global files_to_skip
    files_to_skip = dir_skip_list

    for p in prefix_need_replace:
        # mass_replace(".", p)
        pat = "([^\w])(" + p + ')(\w{1,2})'
        # mass_replace(".", pat)
        # mass_replace("/Users/james/Project/cocos2d-x/cocos2dx", pat)
        mass_replace(dir, pat)
        pat = "(^)(" + p + ')(\w{1,2})'
        # mass_replace(".", pat)
        # mass_replace("/Users/james/Project/cocos2d-x/cocos2dx", pat)
        mass_replace(dir, pat)


def main():
    """
    """
    from optparse import OptionParser

    parser = OptionParser("usage: %prog format-cpp -d DIR_NAME [-s FILES_TO_SKIP]")
    parser.add_option("-d", "--dir",
                      action="store", type="string", dest="dir_name",
                      help="Cpp files in Directory to format")

    parser.add_option("-s", "--skip",
                      action="append", type="string", dest="skips", default=None,
                      help="Files to skip")

    (options, args) = parser.parse_args(sys.argv)

    # print options

    if options.dir_name == None:
        raise Exception("Please set dir by \"-d\" or \"--dir\", run format-cpp -h for the usage.")

    do_replace(options.dir_name, options.skips)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print e
        sys.exit(1)
