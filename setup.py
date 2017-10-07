from setuptools import setup, find_packages

def read(fpath):
    with open(fpath, 'r') as f:
        return f.read()

def requirements(fpath):
    return list(filter(bool, read(fpath).split('\n')))

def version(fpath):
    return read(fpath).strip()

setup(
    name = 'yatr',
    version = version('version.txt'),
    author = 'Matt Bodenhamer',
    author_email = 'mbodenhamer@mbodenhamer.com',
    description = 'Yet Another Task Runner',
    long_description = read('README.rst'),
    url = 'https://github.com/mbodenhamer/yatr',
    packages = find_packages(),
    install_requires = requirements('requirements.in'),
    entry_points = {
        'console_scripts': [
            'yatr = yatr.main:main',
        ]
    },
    license = 'MIT',
    keywords = ['task', 'make', 'yaml'],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities'
    ]
)
