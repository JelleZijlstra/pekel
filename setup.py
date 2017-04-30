import ast
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


requirements = ['six']
if sys.version_info < (3, 5):
    requirements.append('typing')

_current_dir = os.path.abspath(os.path.join(__file__, os.pardir))
_version_re = re.compile(r'__version__\s+=\s+(?P<version>.*)')

with open(os.path.join(_current_dir, 'pekel/__init__.py'), 'r') as f:
    version = _version_re.search(f.read()).group('version')
    version = str(ast.literal_eval(version))

with open(os.path.join(_current_dir, 'README'), 'r') as ld_file:
    long_description = ld_file.read()


if __name__ == '__main__':
    setup(
        name='pekel',
        version=version,
        description="A portable serialization protocol.",
        long_description=long_description,
        keywords='pickle serialization portability',
        author='Jelle Zijlstra',
        author_email='jelle.zijlstra@gmail.com',
        url='https://github.com/JelleZijlstra/pekel',
        license='Apache Software License',
        packages=['pekel'],
        test_suite='tests.test_pekel',
        install_requires=requirements,
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
        ],
    )
