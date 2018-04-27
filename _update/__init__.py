import decorators
import shutil
import os
import sys

@decorators.profiler('_update')
def update(downloadURL):

    import requests
    import zipfile

    # determine if application is a script file or frozen exe
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = sys.path[0]

    download_path = os.path.join(application_path, 'downloading')
    print('download_path', download_path)
    if not os.path.exists(download_path):
        os.mkdir(download_path)

    #  download the distributed package
    cert_path = os.path.abspath(os.path.join(application_path, 'cacert.pem'))
    r = requests.get(downloadURL, verify=cert_path)

    #  save package to download dir
    path_to_zip_file = os.path.join(download_path, 'download.zip')
    print('path_to_zip_file', path_to_zip_file)
    with open(path_to_zip_file, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)

    #  unpack downloaded package
    zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
    root_in_zip = zip_ref.namelist()[0]
    zip_ref.extractall(download_path)
    zip_ref.close()
    os.remove(path_to_zip_file)
    # sys.exit(0)


    print('Copy', os.path.join(download_path, root_in_zip), application_path)
    try:
        copytree(os.path.join(download_path, root_in_zip), application_path)
    except ValueError as err:
        print(err.args)
        sys.exit(1)

    print('Removing', download_path)
    shutil.rmtree(download_path, ignore_errors=False)
    print('\nRestarting after update...\n')
    python = sys.executable
    os.execl(python, python, * sys.argv)



def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    errors = 0
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                try:
                    print('copy2', s, '=>>', d)
                    shutil.copy2(s, d)
                except Exception as e:
                    errors += 1
                    print(e, 'cant overwrite %s', d)
    if errors:
        raise ValueError('Problem with moving files into place', errors)




# requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
