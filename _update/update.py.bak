import os
import sys
import requests
import zipfile
import shutil

# requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

download_path = os.path.join(application_path, 'downloading')
if not os.path.exists(download_path):
    os.mkdir(download_path)

#  download the distributed package
downloadURL = 'https://github.com/Piletilevi/printsrv3/raw/8a19e3531a91d77dfa14f51425e6b9ed3bc98df5/plevi.zip'
# r = requests.get(downloadURL, verify=False)
cert_path = os.path.abspath(os.path.join(application_path, 'cacert.pem'))
r = requests.get(downloadURL, verify=cert_path)

#  save package to download dir
path_to_zip_file = os.path.join(download_path, 'download.zip')
with open(path_to_zip_file, 'wb') as fd:
    for chunk in r.iter_content(chunk_size=128):
        fd.write(chunk)

#  unpack downloaded package
zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
zip_ref.extractall(download_path)
zip_ref.close()
os.remove(path_to_zip_file)

#  update packaged files
# for root, subdirs, files in os.walk(download_path):
#     print('--\nroot = ' + root)
#     rel_path = os.path.relpath(root, download_path)
#     print('\nrelpath = ' + rel_path)
#     target_path = os.path.normpath(os.path.join(application_path, rel_path))
#     print('\ntargetpath = ' + target_path)
#
#     for filename in files:
#         source_file_path = os.path.join(root, filename)
#         target_file_path = os.path.join(target_path, filename)
#         # copy files and meta
#         shutil.copy2(source_file_path, target_file_path))


def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                try:
                    shutil.copy2(s, d)
                except Exception as e:
                    print('cant overwrite %s', d)


copytree(download_path, application_path)
shutil.rmtree(download_path, ignore_errors=False)
