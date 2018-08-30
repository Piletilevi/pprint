# This Python file uses the following encoding: utf-8

import decorators
import random
import sys
import os
import csv
import yaml
import datetime
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import pyqrcode


T_FORENAME = 'eesnimi'
T_SURNAME = 'perenimi'
T_COMPANY1 = 'lisainfo'
T_COMPANY2 = 'lisainfo2'
T_GROUP = 'kaardigrupp'
T_FACE = 'pildifail'
T_QRCODE = 'kood'

K_GRUPP = {
    'Meeskond': 'meeskond',
    'Meeskond (söögiga)': 'meeskond_s',
    'Esineja': 'esineja',
    'Esineja (söögiga)': 'esineja_s',
    'Press': 'press',
    'Press (söögiga)': 'press_s',
    'Meeskond Super': 'meeskond_super'
}


@decorators.profiler('_card')
def card(PLP_JSON_DATA):
    print("inside", __name__)

    def getCenterOffset(draw, text, x, y, font):
        w, h = draw.textsize(text, font=font)
        print('offsetting ', x, w//2, '=', x-w//2)
        return (x-w//2, y)

    def getColorTuple(o):
        if 'color' in o:
            return (o['color']['R'],
                    o['color']['G'],
                    o['color']['B'])
        else:
            return (0, 0, 0)

    def getFont(font):
        return ImageFont.truetype(font['face'] + '.ttf', font['size_pt'])

    rnd = random.getrandbits(4)  # 0..15
    if rnd > 10:
        raise ValueError('''
            Card print failed. Random number generator returned "{rnd}"
            .'''.format(rnd=rnd))
    if PLP_JSON_DATA.get(
        'cardData', {}).get(
            'cards', False) is False:
        raise ValueError('''
            Card print failed. Missing "cards" section in PLP
            .''')

    def printCard(card):
        print('Printing:', card)
        bg_fn = os.path.join(confdir, K_GRUPP[card[T_GROUP]] + '.png')
        layout_fn = os.path.join(confdir, K_GRUPP[card[T_GROUP]] + '.yaml')
        out_fn = os.path.join(outdir, card[T_QRCODE]+'.png')

        with open(layout_fn, 'r', encoding='utf-8') as layout_file:
            layout = yaml.load(layout_file)

        bg_img = Image.open(bg_fn)

        if T_FACE in card and card[T_FACE]:
            face_fn = os.path.join(facesdir, card[T_FACE]+'.png')
            face_img = Image.open(face_fn)
            face_offset = (layout['face']['x'], layout['face']['y'])
            bg_img.paste(face_img, face_offset)

        draw = ImageDraw.Draw(bg_img)

        name_font = getFont(layout['name']['font'])
        name_align = layout['name'].get('align', 'left')
        name_color = getColorTuple(layout['name'])
        if 'surname' in layout['name']:
            surname_color = getColorTuple(layout['name']['surname'])
            surname_font = getFont(layout['name']['font'])
            if 'font' in layout['name']['surname']:
                surname_font = getFont(layout['name']['surname']['font'])
            if name_align == 'center':
                name_offset = getCenterOffset(
                    draw, card[T_FORENAME],
                    layout['name']['x'], layout['name']['y'],
                    name_font
                )
                surname_offset = getCenterOffset(
                    draw, card[T_SURNAME],
                    layout['name']['surname']['x'], layout['name']['surname']['y'],
                    surname_font)
            else:
                name_offset = (layout['name']['x'], layout['name']['y'])
                surname_offset = (layout['name']['surname']['x'],
                                  layout['name']['surname']['y'])
            draw.text(name_offset, card[T_FORENAME], name_color, font=name_font)

            draw.text(surname_offset,
                      card[T_SURNAME],
                      surname_color,
                      font=surname_font)
        else:
            if name_align == 'center':
                name_offset = getCenterOffset(
                    draw, card[T_FORENAME] + ' ' + card[T_SURNAME],
                    layout['name']['x'], layout['name']['y'],
                    name_font
                )
            draw.text(name_offset,
                      card[T_FORENAME] + ' ' + card[T_SURNAME],
                      name_color, font=name_font)

        comp_font = getFont(layout['company1']['font'])
        comp_offset = (layout['company1']['x'], layout['company1']['y'])
        comp_color = (0, 0, 0)
        draw.text(comp_offset, card[T_COMPANY1], comp_color, font=comp_font)

        qrcode = pyqrcode.create(
            card[T_QRCODE],
            error='H',
            version=1,
            mode='numeric'
            )
        qrcode.png(
            tmp_code_fn,
            scale=6,
            module_color=[0, 0, 0, 0],
            background=[0xff, 0xff, 0xff]
            )
        qr_img = Image.open(tmp_code_fn).convert("RGBA")
        qr_code_offset = (layout['qr']['code']['x'], layout['qr']['code']['y'])
        bg_img.paste(qr_img, qr_code_offset)
        qr_text_offset = (layout['qr']['text']['x'], layout['qr']['text']['y'])
        qr_font = getFont(layout['qr']['text']['font'])
        qr_color = getColorTuple(layout['qr']['text'])
        draw.text(qr_text_offset,
                  card[T_QRCODE],
                  qr_color, font=qr_font)
        bg_img.save(out_fn)

    # Setup
    exedir = os.path.dirname(sys.argv[0])
    outdir = os.path.join(
        exedir, 'out',
        datetime.datetime.now().isoformat()
        .replace('T', '_').replace('-', '').replace(':', '')
        .split('.')[0]
    )
    if not os.path.exists(os.path.join(exedir, 'out')):
        os.mkdir(os.path.join(exedir, 'out'))
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    confdir = os.path.join(exedir, 'configuration')
    facesdir = os.path.join(exedir, 'faces')
    tmp_code_fn = os.path.join(exedir, 'code.png')

    # Main
    with open(sys.argv[1], newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        firstrow = True
        labels = 'foo'
        for row in csvreader:
            if firstrow:
                labels = list(map(str.strip, row))
                firstrow = False
            else:
                values = list(map(str.strip, row))
                card = dict(zip(labels, values))
                printCard(card)

    # Cleanup
    # os.rename(datafile_fn, os.path.join(outdir, datafile_bn))
    os.remove(tmp_code_fn)
