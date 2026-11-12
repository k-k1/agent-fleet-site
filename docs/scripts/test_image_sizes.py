#!/usr/bin/env python3
"""Tests for the image sizes: to_starlight.image_size and check_dist.unsized_images.

    python3 -m unittest discover -s docs/scripts -p 'test_*.py'
"""
import struct
import tempfile
import unittest
from pathlib import Path

import check_dist as C
import to_starlight as T


def png(w, h):
    return b'\x89PNG\r\n\x1a\n' + struct.pack('>I', 13) + b'IHDR' + struct.pack('>II', w, h) + b'\x08\x02\x00\x00\x00'


def riff(chunk, payload):
    body = b'WEBP' + chunk + struct.pack('<I', len(payload)) + payload
    return b'RIFF' + struct.pack('<I', len(body)) + body


def vp8x(w, h):
    return riff(b'VP8X', b'\x00\x00\x00\x00' + (w - 1).to_bytes(3, 'little') + (h - 1).to_bytes(3, 'little'))


def vp8(w, h):
    return riff(b'VP8 ', b'\x00\x00\x00' + b'\x9d\x01\x2a' + struct.pack('<HH', w, h) + b'\x00' * 8)


def vp8l(w, h):
    bits = (w - 1) | ((h - 1) << 14)
    return riff(b'VP8L', b'\x2f' + struct.pack('<I', bits) + b'\x00' * 8)


class ImageSize(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def file(self, name, data):
        p = self.dir / name
        (p.write_bytes if isinstance(data, bytes) else p.write_text)(data)
        return p

    def size(self, name, data):
        return T.image_size(self.file(name, data))

    def fails(self, name, data):
        with self.assertRaises(T.ImageSizeError) as cm:
            self.size(name, data)
        self.assertIn(name, str(cm.exception))  # the build names the file

    def test_raster(self):
        self.assertEqual(self.size('a.png', png(1200, 640) + b'\x00' * 4), (1200, 640))
        self.assertEqual(self.size('x.webp', vp8x(1509, 125)), (1509, 125))
        self.assertEqual(self.size('8.webp', vp8(773, 1269)), (773, 1269))
        self.assertEqual(self.size('l.webp', vp8l(19, 13)), (19, 13))
        self.assertIsNone(self.size('a.gif', b'GIF89a'))

    def test_truncated_or_malformed_raster_fails(self):
        for n in (8, 16, 23):
            self.fails(f'short{n}.png', png(1200, 640)[:n])
        self.fails('zero.png', png(0, 640))
        self.fails('jpeg.png', b'\xff\xd8\xff\xe0' + b'\x00' * 40)
        self.fails('short-x.webp', vp8x(100, 50)[:24])
        self.fails('short-x2.webp', vp8x(100, 50)[:29])
        self.fails('short-l.webp', vp8l(100, 50)[:22])
        self.fails('nosig-l.webp', vp8l(100, 50)[:20] + b'\x00' + vp8l(100, 50)[21:])
        self.fails('short-8.webp', vp8(100, 50)[:28])
        self.fails('nostart-8.webp', vp8(100, 50)[:23] + b'\x00\x00\x00' + vp8(100, 50)[26:])
        self.fails('riff.webp', b'RIFF\x00\x00\x00\x00WAVEfmt ' + b'\x00' * 20)
        self.fails('alph.webp', riff(b'ALPH', b'\x00' * 20))

    def test_chunk_and_riff_lengths(self):
        good = vp8x(100, 50)
        zero = good[:16] + b'\x00\x00\x00\x00' + good[20:]  # VP8X chunk of length 0
        self.fails('zero-x.webp', zero)
        lossless = vp8l(100, 50)
        self.fails('short-len-l.webp', lossless[:16] + struct.pack('<I', 4) + lossless[20:])  # VP8L minimum is 5
        long_chunk = good[:16] + struct.pack('<I', 999) + good[20:]  # declared past the RIFF size
        self.fails('long-x.webp', long_chunk)
        self.fails('riff-past-end.webp', good[:4] + struct.pack('<I', 9999) + good[8:])
        self.fails('cut.webp', vp8(100, 50)[:-4])
        self.assertEqual(self.size('padded.webp', good + b'\x00\x00'), (100, 50))  # trailing bytes are fine

    def test_png_needs_the_whole_ihdr(self):
        whole = png(1200, 640) + b'\x00\x00\x00\x00'  # + CRC: 33 bytes
        self.assertEqual(self.size('ok.png', whole), (1200, 640))
        for n in (24, 29, 32):
            self.fails(f'cut{n}.png', whole[:n])

    def test_svg_units(self):
        box = 'viewBox="0 0 200 100"'
        self.assertEqual(self.size('in.svg', f'<svg width="1in" height=".5in" {box} />'), (96, 48))
        self.assertEqual(self.size('cm.svg', f'<svg width="2.54cm" height="25.4mm" {box} />'), (96, 96))
        self.assertEqual(self.size('pt.svg', f"<svg width='72pt' height='6pc' />"), (96, 96))
        self.assertEqual(self.size('px.svg', f'<svg width="300px" height="150" {box} />'), (300, 150))

    def test_svg_viewbox_only_when_absent_or_percent(self):
        self.assertEqual(self.size('box.svg', '<?xml version="1.0"?><svg xmlns="x" viewBox="0 0 400 300" />'), (400, 300))
        self.assertEqual(self.size('pct.svg', '<svg width="100%" height="100%" viewBox="0,0,400,300" />'), (400, 300))
        self.assertEqual(self.size('w.svg', '<svg width="2in" viewBox="0 0 400 300" />'), (192, 144))
        self.assertEqual(self.size('h.svg', '<svg width="50%" height="150" viewBox="0 0 400 300" />'), (200, 150))
        self.assertEqual(self.size('tiny.svg', '<svg width="0.4" height="0.3" />'), (1, 1))

    def test_svg_that_cannot_be_sized_fails(self):
        self.fails('em.svg', '<svg width="10em" height="5em" viewBox="0 0 200 100" />')
        self.fails('none.svg', '<svg xmlns="x" />')
        self.fails('pctonly.svg', '<svg width="100%" height="50%" />')
        self.fails('badbox.svg', '<svg viewBox="0 0 0 100" />')
        self.fails('nosvg.svg', '<html></html>')
        self.fails('broken.svg', '<svg width="10" height="10">')

    def test_svg_root_not_a_comment_or_cdata(self):
        self.assertEqual(self.size('c.svg', '<!-- <svg width="900" height="100"> --><svg width="100" height="100" />'),
                         (100, 100))
        self.assertEqual(self.size('pi.svg', '<?xml version="1.0"?>\n<!-- note -->\n<?x <svg width="9" height="9"> ?>'
                                   '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="20">'
                                   '<style><![CDATA[ <svg width="900" height="900"> ]]></style></svg>'), (40, 20))
        self.assertEqual(self.size('dt.svg', '<?xml version="1.0"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
                                   '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg width="5" height="6"/>'),
                         (5, 6))
        self.fails('html-root.svg', '<html><svg width="10" height="10"/></html>')

    def test_svg_entities_and_internal_dtd_are_refused(self):
        self.fails('ent.svg', '<!DOCTYPE svg [<!ENTITY w "900">]><svg width="&w;" height="10"/>')
        self.fails('subset.svg', '<!DOCTYPE svg [ ]><svg width="10" height="10"/>')


def page(content, chrome=''):
    return (f'<html><body><header>{chrome}</header><main><div class="sl-markdown-content">{content}</div>'
            '<footer><img src="/f.png"></footer></main></body></html>')


class UnsizedImages(unittest.TestCase):
    def test_sized(self):
        for tag in ('<img src="a" width="10" height="5">', "<img src='a' width='100' height='50'>",
                    '<img src="a" width=10 height=5 />', '<img src="a" style="width: 100%; aspect-ratio: 16 / 9">',
                    '<img src="a" style="aspect-ratio: auto; aspect-ratio: 1.5">', '<img src="a" style="aspect-ratio: auto 4/3">',
                    '<img src="a" style="ASPECT-RATIO: .5 !important">',
                    '<img src="a" alt="Settings > Agents" width="10" height="5">'):
            self.assertEqual(C.unsized_images(page(tag)), [], tag)

    def test_unsized(self):
        for tag in ('<img src="a" width="10">', '<img src="a" alt="aspect-ratio: 1" width="10">',
                    '<img src="a" title="height=5" width="10">', '<img src="a" width="10" height="0">',
                    '<img src="a" width="10" height="">', '<img src="a" style="aspect-ratio: auto">',
                    '<img src="a" alt="a > b" width="10">', '<img src="a" style="aspect-ratio: garbage">',
                    '<img src="a" style="aspect-ratio: 16/9; aspect-ratio: auto">', '<img src="a" style="aspect-ratio: 0">',
                    '<img src="a" style="aspect-ratio: 16 / 0">', '<img src="a" style="aspect-ratio: -1">',
                    '<img src="a" style="aspect-ratio:">', '<img src="a" style="aspect-ratio: 1/2/3">',
                    '<img src="a" width="inf" height="5">'):
            self.assertEqual(len(C.unsized_images(page(tag))), 1, tag)

    def test_nested_content_is_checked(self):
        tag = '<img src="a" width="10">'
        for wrap in ('<table><tr><td>{}</td></tr></table>', '<aside class="starlight-aside"><p>{}</p></aside>',
                     '<p>text {} text<br>more</p>', '<figure><picture><source srcset="b">{}</picture></figure>'):
            self.assertEqual(len(C.unsized_images(page(wrap.format(tag)))), 1, wrap)

    def test_chrome_and_comments_are_skipped(self):
        chrome = '<a href="/"><img class="logo" src="/logo.svg" alt=""></a>'
        content = '<p>x</p><!-- <img src="old.webp" width="10"> --><p>y</p>'
        self.assertEqual(C.unsized_images(page(content, chrome)), [])


if __name__ == '__main__':
    unittest.main()
