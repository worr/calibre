#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai

__license__   = 'GPL v3'
__copyright__ = '2010, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

import os, textwrap, re, subprocess

INC = '/usr/include/ImageMagick'

'''
Various constants defined in the ImageMagick header files. Note that
they are defined as actual numeric constants rather than symbolic names to
ensure that the extension can be compiled against older versions of ImageMagick
than the one this script is run against.
'''

def parse_enums(f):
    print '\nParsing:', f
    raw = open(os.path.join(INC, f)).read()
    raw = re.sub(r'(?s)/\*.*?\*/', '', raw)
    raw = re.sub('#.*', '', raw)

    for enum in re.findall(r'typedef\s+enum\s+\{([^}]+)', raw):
        enum = re.sub(r'(?s)/\*.*?\*/', '', enum)
        for x in enum.splitlines():
            e = x.split(',')[0].strip().split(' ')[0]
            if e:
                val = get_value(e)
                print e, val
                yield e, val

def get_value(const):
    t = '''
    #include <wand/MagickWand.h>
    #include <stdio.h>
    int main(int argc, char **argv) {
    printf("%%d", %s);
    return 0;
    }
    '''%const
    with open('/tmp/ig.c','wb') as f:
        f.write(t)
    subprocess.check_call(['gcc', '-I/usr/include/ImageMagick', '/tmp/ig.c', '-o', '/tmp/ig', '-lMagickWand'])
    return int(subprocess.Popen(["/tmp/ig"],
        stdout=subprocess.PIPE).communicate()[0].strip())


def main():
    constants = []
    for x in ('resample', 'image', 'draw', 'distort'):
        constants += list(parse_enums('magick/%s.h'%x))
    base = os.path.dirname(__file__)
    constants = [
        'PyModule_AddIntConstant(m, "{0}", {1});'.format(c, v) for c, v in
            constants]
    raw = textwrap.dedent('''\
        // Generated by generate.py

        static void magick_add_module_constants(PyObject *m) {
            %s
        }
        ''')%'\n    '.join(constants)
    with open(os.path.join(base, 'magick_constants.h'), 'wb') as f:
        f.write(raw)


if __name__ == '__main__':
    main()
