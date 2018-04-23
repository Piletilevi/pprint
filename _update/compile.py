from distutils.core import setup
import sys
import shutil
import py2exe
import requests.certs

build_exe_options = {"include_files": [(requests.certs.where(), 'cacert.pem')]}
sys.argv.append('py2exe')

dist_dir = 'dist'
shutil.rmtree(dist_dir, ignore_errors=True)

OPTIONS = [
    {
        "script": "update.py",
        "dest_base": "updater",
        "include_files": [(requests.certs.where(), 'cacert.pem')]
    }
]

setup(
    # cmdclass={"py2exe": JsonSchemaCollector},
    options={
        'py2exe': {
            'bundle_files': 3,
            'dist_dir': dist_dir,
            'includes': [
                'requests', 'zipfile', 'queue'],
            'excludes': ['tkinter'],
        }
    },
    zipfile=None,  # 'update-lib.zip',
    windows=OPTIONS,
    # console = OPTIONS,
    data_files=[
        ('.', ['package.json', 'cacert.pem'])
    ],
)
