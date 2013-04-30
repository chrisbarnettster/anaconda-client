'''
Add a new package to your account.
'''
from binstar_client.utils import get_binstar, parse_specs
from argparse import FileType
from os.path import basename
import tarfile
import json

def detect_conda_attrs(file):
    tar = tarfile.open(file)
    obj = tar.extractfile('info/index.json')
    return json.loads(obj.read())

detectors = {'conda':detect_conda_attrs}
def detect(binstar, user, package, file):
    
    package_type = binstar.package(user, package).get('package_type')
    func = detectors.get(package_type, lambda file:{})
    attrs = func(file)
    return attrs

def main(args):
    
    binstar = get_binstar()
    spec = args.spec
    if args.action == 'upload':
        for file in args.files:
            attrs = detect(binstar, spec.user, spec.package, file)
            with open(file) as fd:
                print 'Uploading %s ... ' % file
                binstar.upload(spec.user, spec.package, spec.version, basename(file), fd, args.description, **attrs)
        print '... done'
    elif args.action == 'download':
        fd = binstar.download(spec.user, spec.package, spec.version, spec.basename)
        
        if args.files:
            fname = args.files[0]
        data = fd.read()
        with open(fname, 'w') as fdout:
            fdout.write(data)
    elif args.action == 'list':
        release = binstar.release(spec.user, spec.package, spec.version)
        for dist in release.get('distributions',[]):
            print '%(basename)s id: %(_id)s' % dist 
            for key_value in dist['attrs'].items():
                print '  + %s: %r' % key_value
    elif args.action == 'remove':
        print spec.user, spec.package, spec.version, spec.basename, spec.attrs
        print binstar.remove_dist(spec.user, spec.package, spec.version, spec.basename, spec.attrs)
    else:
        raise NotImplementedError(args.action)
    

def add_parser(subparsers):
    
    parser = subparsers.add_parser('dist',
                                      help='Add a release',
                                      description=__doc__)
    
    parser.add_argument('action', help='Adde remove or update an existing release',
                        choices=['upload', 'download', 'remove', 'list'])
    parser.add_argument('spec', help='Package written as <user>/<package>/<version>', type=parse_specs)
    parser.add_argument('files', nargs='*', help='Distributions to upload', default=[])
    parser.add_argument('-d','--description', help='description of the file(s)')
    
    parser.set_defaults(main=main)
    
    


