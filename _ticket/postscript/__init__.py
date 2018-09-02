# This Python file uses the following encoding: utf-8

import decorators

import os
import sys
import win32ui
import win32gui
import win32print
import requests
import math
import yaml

import collections
import ctypes
import time

from code128image import code128_image as _c128image
from PIL import ImageWin
from PIL import Image

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = sys.path[0]


def ordered_load(stream, Loader=yaml.Loader,
                 object_pairs_hook=collections.OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


# @decorators.profiler('_ticket')
class PSPrint:
    @decorators.profiler('_ticket')
    def __init__(self, plp_json_data):
        if getattr(sys, 'frozen', False):
            self.BASEDIR = os.path.dirname(sys.executable)
        else:
            self.BASEDIR = sys.path[0]

        self.PLP_JSON_DATA = plp_json_data
        # chdir(self.BASEDIR)

        prnt = self.PLP_JSON_DATA['ticketData']['printerData']['printerName']
        try:
            self.hprinter = win32print.OpenPrinter(prnt)
        except Exception as e:
            raise ValueError('Can not open "{prnt}".'.format(prnt=prnt))

        try:
            devmode = win32print.GetPrinter(self.hprinter, 2)['pDevMode']
        except Exception as e:
            raise ValueError('Can not register "{prnt}".'.format(prnt=prnt))

        try:
            devmode.Orientation = 2
        except Exception as e:
            raise ValueError('Can not set orientation for "{prnt}".'
                             .format(prnt=prnt))

        self._waitForSpooler(1, 'Printer has queued jobs', 'Проверь принтер!')

        try:
            self.DEVICE_CONTEXT_HANDLE = win32gui.CreateDC('WINSPOOL', prnt,
                                                           devmode)
        except Exception as e:
            raise ValueError('Failed DCH "{prnt}".'.format(prnt=prnt))

        try:
            self.DEVICE_CONTEXT = win32ui.CreateDCFromHandle(
                self.DEVICE_CONTEXT_HANDLE)
        except Exception as e:
            raise ValueError('Failed DC "{prnt}".'.format(prnt=prnt))

        layout_fn = os.path.join(self.BASEDIR, 'config', 'layout.yaml')
        with open(layout_fn, 'r', encoding='utf-8') as layout_file:
            self.PS_LAYOUT = ordered_load(layout_file, yaml.SafeLoader)

    def __enter__(self):
        print('Enter PSPrint')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._waitForSpooler(2, '''
            - Включен ли принтер?\n
            - Подключен ли принтер к компьютеру?\n
            - Правильно ли вставлены билетные бланки в принтер?''',
                             'Проверь принтер!')

    def _waitForSpooler(self, sleep_sec, message, title):
        printjobs = win32print.EnumJobs(self.hprinter, 0, 999)
        if len(printjobs) != 0:
            time.sleep(sleep_sec)
            printjobs = win32print.EnumJobs(self.hprinter, 0, 999)
            i = 3
            while len(printjobs) != 0 and i > 0:
                i -= 1
                ctypes.windll.user32.MessageBoxW(0, message, title, 0)
                printjobs = win32print.EnumJobs(self.hprinter, 0, 999)

    def _setFont(self, font_name, w=None, h=None, weight=None, orientation=0):
        if font_name is not None:
            _log_font = [font_name]

            def callback(font, tm, fonttype, _font):
                if font.lfFaceName == _font[0]:
                    _font[0] = font
                return True
            win32gui.EnumFontFamilies(self.DEVICE_CONTEXT_HANDLE, None,
                                      callback, _log_font)
            self.log_font = _log_font[0]

        self.log_font.lfWidth = int(w)
        self.log_font.lfHeight = int(h)
        self.log_font.lfWeight = int(weight)
        self.log_font.lfOrientation = int(orientation) * 10
        self.log_font.lfEscapement = int(orientation) * 10
        font_handle = win32gui.CreateFontIndirect(self.log_font)
        win32gui.SelectObject(self.DEVICE_CONTEXT_HANDLE, font_handle)

    def _placeText(self, x, y, text):
        ctypes.windll.gdi32.TextOutW(self.DEVICE_CONTEXT_HANDLE, x, y,
                                     text, len(text))

    def _indexedRotate(self, degrees):
        return math.floor((degrees % 360) / 90 + 0.5)

    def _rotatePicture(self, _pic, degrees):
        if degrees % 360 == 0:
            return _pic

        _temp_fn = '{0}_{1}.png'.format(os.path.join(self.BASEDIR, 'img',
                                                     'temprotate'), degrees)
        _pic = _pic.transpose((self._indexedRotate(degrees) - 1) % 3 + 2)
        _pic.save(_temp_fn, 'png')
        _pic = Image.open(_temp_fn)
        return _pic

    def _placeImage(self, x, y, url, rotate):
        _picture_fn = '{0}_{1}.png'.format(
            os.path.join(self.BASEDIR, 'img', os.path.basename(url)), rotate)
        if not os.path.isfile(_picture_fn):
            cert_path = os.path.abspath(os.path.join(application_path, 'certifi', 'cacert.pem'))
            r = requests.get(url, verify=cert_path)
            r.raise_for_status()

        with open(_picture_fn, 'wb') as fd:
            # print('with ', _picture_fn)
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
        _pic = self._rotatePicture(Image.open(_picture_fn), rotate)

        # print('save')
        _pic.save(_picture_fn, 'PNG')

        _pic = Image.open(_picture_fn)
        dib = ImageWin.Dib(_pic)
        dib.draw(self.DEVICE_CONTEXT_HANDLE,
                 (x, y, x + _pic.size[0], y + _pic.size[1]))

    def _placeC128(self, text, x, y,
                   width, height, thickness, rotate, quietzone):
        file1 = '{0}_1_{1}.png'.format(
            os.path.join(self.BASEDIR, 'img', 'tmp'), rotate)
        _c128image(
            text, int(width), int(height), quietzone).save(file1, 'JPEG')
        _pic = self._rotatePicture(Image.open(file1), rotate)
        dib = ImageWin.Dib(_pic)
        dib.draw(self.DEVICE_CONTEXT_HANDLE,
                 (x, y, x + _pic.size[0], y + _pic.size[1]))

    def _startDocument(self):
        # print("DEVICE_CONTEXT.SetMapMode")
        self.DEVICE_CONTEXT.SetMapMode(1)
        # print("DEVICE_CONTEXT.StartDoc")
        self.DEVICE_CONTEXT.StartDoc("ticket.txt")
        # print("DEVICE_CONTEXT.StartPage")
        self.DEVICE_CONTEXT.StartPage()
        # print("win32ui.CreateFont");
        font = win32ui.CreateFont({"name": "Arial", "height": 16})
        # print("DEVICE_CONTEXT.SelectObject")
        self.DEVICE_CONTEXT.SelectObject(font)
        # print("DEVICE_CONTEXT.SelectObject DONE")

    def _printDocument(self):
        self.DEVICE_CONTEXT.EndPage()
        self.DEVICE_CONTEXT.EndDoc()

    @decorators.profiler('_ticket.printTickets')
    def printTickets(self):
        for ticket in self.PLP_JSON_DATA['ticketData']['tickets']:
            self._startDocument()
            self.printTicket(ticket)
            self._printDocument()

    def _getInstanceProperty(self, key, instance, field, mandatory=False):
        if key in instance:
            return instance.get(key)
        if key in field.get('common', []):
            return field.get('common').get(key)
        # if mandatory:
        #     print('Text without {0} - {1}'.format(key, field))
        return None

    def printTicket(self, ticket):
        # Load ticket layout file
        default_lo_url = 'https://raw.githubusercontent.com/Piletilevi/pprint/master/config/layout.yaml'
        layout_url = ticket.get('ticketLayoutUrl', default_lo_url)
        layout_fn = os.path.join(self.BASEDIR, 'config',
                                 os.path.basename(layout_url))
        if not os.path.isfile(layout_fn):
            cert_path = os.path.abspath(os.path.join(application_path, 'certifi', 'cacert.pem'))
            r = requests.get(layout_url, verify=cert_path)
            r.raise_for_status()

        with open(layout_fn, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)

        with open(layout_fn, 'r', encoding='utf-8') as layout_file:
            ps_layout = ordered_load(layout_file, yaml.SafeLoader)

        for layout_key in ps_layout.keys():
            # print('layout_key : {0}'.format(layout_key))
            field = ps_layout[layout_key]
            value = ticket.get(
                layout_key, self.PLP_JSON_DATA.get(layout_key, ''))
            if value == '':
                # print('skip layout_key {0}'.format(layout_key))
                continue

            if field['type'] == 'text':
                for instance in field['instances']:
                    font_name   = self._getInstanceProperty('font_name', instance, field)
                    font_height = self._getInstanceProperty('font_height', instance, field)
                    font_width  = self._getInstanceProperty('font_width', instance, field)
                    font_weight = self._getInstanceProperty('font_weight', instance, field)
                    x           = self._getInstanceProperty('x', instance, field)
                    y           = self._getInstanceProperty('y', instance, field)
                    if not (font_height and font_width and font_weight and x and y):
                        continue
                    orientation = self._getInstanceProperty('orientation', instance, field)     or 0
                    prefix      = self._getInstanceProperty('prefix', instance, field) or ''
                    suffix      = self._getInstanceProperty('suffix', instance, field) or ''
                    self._setFont(font_name, font_width, font_height, font_weight, orientation)
                    self._placeText(int(x), int(y), '{0}{1}{2}'.format(prefix, value, suffix))
                continue

            elif field['type'] == 'image':
                for instance in field['instances']:
                    x           = self._getInstanceProperty('x', instance, field)
                    y           = self._getInstanceProperty('y', instance, field)
                    orientation = self._getInstanceProperty('orientation', instance, field)     or 0
                    self._placeImage(int(x), int(y), value, orientation)
                continue

            elif field['type'] == 'code128':
                for instance in field['instances']:
                    thickness   = self._getInstanceProperty('thickness', instance, field)       or 10
                    width       = self._getInstanceProperty('width', instance, field)           or 560
                    height      = self._getInstanceProperty('height', instance, field)          or 100
                    x           = instance.get('x', field.get('common', {'x': False}).get('x', False))
                    y           = instance.get('y', field.get('common', {'y': False}).get('y', False))
                    orientation = self._getInstanceProperty('orientation', instance, field)     or 0
                    quietzone   = self._getInstanceProperty('quietzone', instance, field)       or False
                    if not (x and y):
                        continue
                    self._placeC128(value, int(x), int(y), width, height, thickness, orientation, quietzone)
                continue