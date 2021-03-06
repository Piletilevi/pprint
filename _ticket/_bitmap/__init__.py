# This Python file uses the following encoding: utf-8

import decorators

import os
import io
import sys
import requests
import math
import yaml
import json
import pyqrcode

import collections

from code128image import code128_image as _c128image
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


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


@decorators.log('')
def log(*args):
    pass


# @decorators.profiler('_bitmap')
class BMPPrint:
    @decorators.profiler('_bitmap')
    def __init__(self, ticket):
        if getattr(sys, 'frozen', False):
            self.BASEDIR = os.path.dirname(sys.executable)
        else:
            self.BASEDIR = sys.path[0]

        self.TICKET = ticket

    def _setFont(self, font_name):
        None

    def _imgPath(self, url, rotate):
        return '{0}_{1}.png'.format(
            os.path.join(self.BASEDIR, 'tmp', os.path.basename(url)), rotate)

    def _placeQR(self, text, x, y, scale,
                 background=None, foreground=None):

        if background is None:
            background = (255, 255, 255, 255)
        else:
            background = dict(background)
            background = (background.get('R', 255),
                          background.get('G', 255),
                          background.get('B', 255),
                          background.get('A', 255))
        if foreground is None:
            foreground = (0, 0, 0, 255)
        else:
            foreground = dict(foreground)
            foreground = (foreground.get('R', 0),
                          foreground.get('G', 0),
                          foreground.get('B', 0),
                          foreground.get('A', 255))

        qrcode = pyqrcode.create(text,
                                 error='H',
                                 version=1,
                                 # mode='numeric'
                                 )
        png_buffer = io.BytesIO()
        qrcode.png(
            png_buffer,
            scale=scale,
            module_color=foreground,
            background=background
            )
        qr_img = Image.open(png_buffer).convert("RGBA")
        self.image.paste(qr_img, (x, y))

    def _placeText(self, font_name,
                   font_size, x, y, text,
                   rotate=0, color=None):
        if color is None:
            color = (0, 0, 0, 255)
        else:
            color = dict(color)
            color = (color.get('R', 0),
                     color.get('G', 0),
                     color.get('B', 0),
                     color.get('A', 255))
        font_fn = os.path.join(self.BASEDIR, 'ttf', font_name+'.ttf')
        font = ImageFont.truetype(font_fn, font_size)
        img_txt = Image.new('RGBA', font.getsize(text),
                            color=(0, 0, 0, 0))
        img_txt.filename = text
        img_drw = ImageDraw.Draw(img_txt)
        img_drw.text((0, 0), text,  font=font, fill=color)
        img_txt = self._rotatePicture(img_txt, rotate)
        transparent_bg = Image.new('RGBA', self.image.size,
                                   color=(0, 0, 0, 0))
        transparent_bg.paste(img_txt, (x, y))
        self.image = Image.alpha_composite(self.image, transparent_bg)
        # self.image.paste(img_txt, (x, y))

    def _indexedRotate(self, degrees):
        rix = {0: 0,
               1: Image.ROTATE_90,
               2: Image.ROTATE_180,
               3: Image.ROTATE_270}
        return rix[math.floor((degrees % 360) / 90 + 0.5)]

    def _rotatePicture(self, _pic, degrees):
        rotate = self._indexedRotate(degrees)
        if rotate == 0:
            return _pic

        _temp_fn = self._imgPath('tmp_' + _pic.filename, rotate)
        _pic = _pic.transpose(rotate)
        _pic.save(_temp_fn, 'png')
        _pic = Image.open(_temp_fn)
        return _pic

    def _placeImage(self, x, y, url, rotate):
        if os.path.basename(url) == '':
            return
        _picture_fn = os.path.join(self.BASEDIR, 'img', os.path.basename(url))
        if not os.path.isfile(_picture_fn):
            cert_path = os.path.abspath(
                os.path.join(self.BASEDIR, 'certifi', 'cacert.pem'))
            r = requests.get(url, verify=cert_path)
            r.raise_for_status()

            with open(_picture_fn, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)

        _pic = self._rotatePicture(Image.open(_picture_fn), rotate)

        transparent_bg = Image.new('RGBA', self.image.size,
                                   color=(0, 0, 0, 0))
        transparent_bg.paste(_pic, (x, y))
        self.image = Image.alpha_composite(self.image, transparent_bg)
        # self.image.paste(_pic, (x, y))

    def _placeC128(self, text, x, y, width, height, thickness, rotate, quietzone):
        _pic = _c128image(text, int(width), int(height), quietzone)
        _pic.filename = 'c128'
        _pic = self._rotatePicture(_pic, rotate)
        self.image.paste(_pic, (x, y))

    def _startDocument(self):
        self.image = Image.new(
            'RGBA',
            (self.page_settings['width']['px'],
             self.page_settings['height']['px']),
            color=(255, 255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)

    def _getInstanceProperty(self, key, instance, field, mandatory=False):
        if key in instance:
            return instance.get(key)
        if key in field.get('common', []):
            return field.get('common').get(key)
        # if mandatory:
        #     print('Text without {0} - {1}'.format(key, field))
        return None

    def _page_setup(self, page):
        res = (page.get('resolution')[0:-3], page.get('resolution')[-3:])
        resolution = float(res[0])  # d/cm
        if res[1] == 'dpi':
            resolution = float(res[0]) / 2.54  # d/cm

        w = (float(page.get('width')[0:-2]), page.get('width')[-2:])
        width = {'mm': w[0]/resolution*10, 'px': int(w[0])}
        if w[1] == 'mm':
            width = {'px': int(w[0]/10*resolution), 'mm': w[0]}

        h = (float(page.get('height')[0:-2]), page.get('height')[-2:])
        height = {'mm': h[0]/resolution*10, 'px': int(h[0])}
        if h[1] == 'mm':
            height = {'px': int(h[0]/10*resolution), 'mm': h[0]}

        return {'resolution': resolution,
                'width': width,
                'height': height,
                'printOrientation': page.get('printOrientation', None)}
        # o = page.get('offset')
        #
        # o_x = (float(o.get('width')[0:-2]), page.get('width')[-2:])
        # offset_width = {'mm': o_x[0]/resolution*10, 'px': int(o_x[0])}
        # if o_x[1] == 'mm':
        #     offset_width = {'px': int(o_x[0]/10*resolution), 'mm': o_x[0]}
        #
        # o_y = (float(o.get('height')[0:-2]), page.get('height')[-2:])
        # offset_height = {'mm': o_y[0]/resolution*10, 'px': int(o_y[0])}
        # if o_y[1] == 'mm':
        #     offset_height = {'px': int(o_y[0]/10*resolution), 'mm': o_y[0]}
        #
        # return {'resolution': resolution, 'width': width, 'height': height, 'offset': {'width': width, 'height': height}}

    @decorators.profiler('_ticket.printTicket')
    def printTicket(self, job_no):
        # Load ticket layout file
        default_lo_fn = 'layout.yaml'
        layout_url = self.TICKET.get('layout', {}).get('url', '')
        layout_fn = self.TICKET.get('layout', {}).get('name', '')
        if layout_fn:
            layout_fn = layout_fn + '.yaml'
        layout_fn = layout_fn or os.path.basename(layout_url) or default_lo_fn
        layout_file_path = os.path.join(self.BASEDIR, 'config', layout_fn)

        if not os.path.isfile(layout_file_path):
            if layout_url:
                cert_path = os.path.abspath(
                    os.path.join(self.BASEDIR, 'certifi', 'cacert.pem'))
                r = requests.get(layout_url, verify=cert_path)

                if r.status_code == requests.codes.ok:
                    with open(layout_file_path, 'wb') as fd:
                        for chunk in r.iter_content(chunk_size=128):
                            fd.write(chunk)
                else:
                    layout_file_path = os.path.join(
                        self.BASEDIR, 'config', default_lo_fn)

        log('layout_file_path', layout_file_path)
        with open(layout_file_path, 'r', encoding='utf-8') as layout_file:
            ps_layout = ordered_load(layout_file, yaml.SafeLoader)

        self.page_settings = self._page_setup(ps_layout.get('Page'))
        log('page_settings', json.dumps(self.page_settings))

        self._startDocument()
        # log('Doc started')

        if isinstance(ps_layout.get('Layout'), list):
            # log('layout is list')
            layouts = ps_layout['Layout']
        else:
            # log('layout is NOT list')
            layouts = [ps_layout['Layout']]

        lo_page_no = 0
        self.out_fn = []
        for layout in layouts:
            lo_page_no += 1
            # log('Laying out page {} of {}'.format(lo_page_no, len(layouts)))
            for layout_key in layout.keys():
                # log('layout_key : {0}'.format(layout_key))
                field = layout.get(layout_key)
                value = self.TICKET.get(
                    layout_key,
                    self.TICKET.get('transactionData', {}).get(layout_key, '')
                )
                if value is None:
                    value = ''
                if value == '':
                    value = field.get('default', '')
                if value == '':
                    log('skip layout_key {0}'.format(layout_key))
                    continue

                for instance in field['instances']:
                    instance_type = self._getInstanceProperty(
                        'type', instance, field)
                    log('({}) {}'.format(instance_type, layout_key))

                    if instance_type == 'text':
                        font_name   = self._getInstanceProperty('font_name', instance, field)
                        font_height = self._getInstanceProperty('font_height', instance, field)
                        font_width  = self._getInstanceProperty('font_width', instance, field)
                        font_weight = self._getInstanceProperty('font_weight', instance, field)
                        x           = self._getInstanceProperty('x', instance, field)
                        y           = self._getInstanceProperty('y', instance, field)
                        if not (font_height and font_width and font_weight and x and y):
                            continue
                        font_color  = self._getInstanceProperty('font_color', instance, field)

                        orientation = self._getInstanceProperty('orientation', instance, field)     or 0
                        prefix      = self._getInstanceProperty('prefix', instance, field) or ''
                        suffix      = self._getInstanceProperty('suffix', instance, field) or ''
                        # self._setFont(font_name, font_width, font_height, font_weight, orientation)
                        self._placeText(font_name, font_height, int(x), int(y),
                                        '{0}{1}{2}'.format(prefix, value, suffix),
                                        orientation, font_color)
                        continue

                    elif instance_type == 'image':
                        x           = self._getInstanceProperty('x', instance, field)
                        y           = self._getInstanceProperty('y', instance, field)
                        orientation = self._getInstanceProperty('orientation', instance, field)     or 0
                        self._placeImage(int(x), int(y), value, orientation)
                        continue

                    elif instance_type == 'code128':
                        thickness   = self._getInstanceProperty('thickness', instance, field)       or 10
                        width       = self._getInstanceProperty('width', instance, field)           or 560
                        height      = self._getInstanceProperty('height', instance, field)          or 100
                        x           = self._getInstanceProperty('x', instance, field)
                        y           = self._getInstanceProperty('y', instance, field)
                        orientation = self._getInstanceProperty('orientation', instance, field)     or 0
                        quietzone   = self._getInstanceProperty('quietzone', instance, field)       or False
                        self._placeC128(value, int(x), int(y), width, height,
                                        thickness, orientation, quietzone)
                        continue

                    elif instance_type == 'qrcode':
                        scale       = self._getInstanceProperty('scale', instance, field)           or 8
                        x           = self._getInstanceProperty('x', instance, field)
                        y           = self._getInstanceProperty('y', instance, field)
                        background  = self._getInstanceProperty('background', instance, field)
                        foreground  = self._getInstanceProperty('foreground', instance, field)
                        self._placeQR(value, int(x), int(y), scale,
                                      background, foreground)
                        continue

            out_fn = os.path.join(self.BASEDIR, 'img',
                                  self.TICKET['ticketId']+'_'+str(lo_page_no)+'.png')
            log('Saving', out_fn)
            self.image.save(out_fn)
            self.out_fn.append(out_fn)
            # log('Saved', 'out_fn')
            log('Saved', out_fn)
