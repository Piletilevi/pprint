# This Python file uses the following encoding: utf-8

import decorators

import os
import sys
import win32ui
import win32gui
import win32print

import ctypes
import time

from PIL import ImageWin
from PIL import Image


# @decorators.profiler('_postscript')
class PSPrint:
    @decorators.profiler('_postscript')
    def __init__(self, printerData):
        if getattr(sys, 'frozen', False):
            self.BASEDIR = os.path.dirname(sys.executable)
        else:
            self.BASEDIR = sys.path[0]

        prnt = printerData['printerName']
        try:
            self.hprinter = win32print.OpenPrinter(prnt)
        except Exception as e:
            raise ValueError('Can not open "{prnt}".'.format(prnt=prnt))

        try:
            devmode = win32print.GetPrinter(self.hprinter, 2)['pDevMode']
        except Exception as e:
            raise ValueError('Can not register "{prnt}".'.format(prnt=prnt))

        try:
            if printerData['printOrientation'] == 'portrait':
                devmode.Orientation = 1
            elif printerData['printOrientation'] == 'landscape':
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

    def _placeImage(self, x, y, img_basename):
        bmp_fn = os.path.join(self.BASEDIR, 'img', img_basename)
        print('place image from', bmp_fn)
        if not os.path.isfile(bmp_fn):
            raise ValueError('Can not open "{bmp_fn}".'.format(bmp_fn=bmp_fn))
        _pic = Image.open(bmp_fn)
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

    def _turnPage(self):
        self.DEVICE_CONTEXT.EndPage()
        self.DEVICE_CONTEXT.StartPage()

    def _printDocument(self):
        self.DEVICE_CONTEXT.EndPage()
        self.DEVICE_CONTEXT.EndDoc()

    @decorators.profiler('_ticket.printTicket')
    def printTicket(self, bmp_fns=None):
        if bmp_fns is None:
            raise ValueError('Missing ticket bitmap file names')

        print('Printing', len(bmp_fns), 'pages.')
        self._startDocument()
        page_no = 0
        for bmp_fn in bmp_fns:
            page_no += 1
            print('Printing from bitmap', bmp_fn)
            self._placeImage(0, 0, bmp_fn)
            if len(bmp_fns) > page_no:
                self._turnPage()
        self._printDocument()
        return
