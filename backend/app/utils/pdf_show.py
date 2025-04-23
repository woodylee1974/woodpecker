import pypdfium2 as pdfium
import os
import io
from PIL import Image, ImageDraw, ImageFont
from typing import Annotated, List, Union


PageBox = Annotated[List[tuple], "[(page_num, [(x, y, left, bottom)*])*]"]
IMAGE_DPI = 72


pdf_cache = None
def get_pdf_cache():
    global pdf_cache
    if pdf_cache is None:
        pdf_cache = PdfCache()
    return pdf_cache


class PdfCache:
    MAX_NUM = 8

    def __init__(self):
        self.cache = {}
        self.keys = []

    def get(self, fn):
        doc = self.cache.get(fn, None)
        if doc is not None:
            self.update_cache(fn, hit=True)
            return doc
        self.update_cache(fn)
        if not fn.startswith("/"):
            abs_fn = os.path.join(os.getcwd(), fn)
        else:
            abs_fn = fn
        ret = self.cache[fn] = pdfium.PdfDocument(abs_fn)
        return ret

    def update_cache(self, fn, hit=False):
        if hit:
            del self.keys[self.keys.index(fn)]
            self.keys.append(fn)
        else:
            if len(self.keys) > PdfCache.MAX_NUM:
                del self.cache[self.keys[0]]
                self.keys.pop(0)
            self.keys.append(fn)


def render_image(filename: str, page_boxes: PageBox, offset: int = None) -> bytes:
    def enlarge_bbox(bbox):
        offset = 4
        return bbox[0] - offset, bbox[1] - offset, bbox[2] + offset, bbox[3] + offset

    if offset is None:
        delta = 0
    else:
        delta = int(offset)
    doc = get_pdf_cache().get(filename)
    pages = [page for page, _ in page_boxes]
    if len(pages) == 0:
        image = doc[0].render(scale=IMAGE_DPI / 72, draw_annots=False).to_pil()
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return buf.getvalue()
    min_page, max_page = min(pages), max(pages)
    page_dict = {p: [] for p in range(min_page, max_page + 1)}
    for page, bbox in page_boxes:
        if bbox is not None:
            page_dict[page].append(bbox)
    page = page_boxes[0][0] + delta

    image = None
    if 0 <= page < len(doc):
        image = doc[page].render(scale=IMAGE_DPI / 72, draw_annots=False).to_pil()
    elif page < 0:
        image = doc[0].render(scale=IMAGE_DPI / 72, draw_annots=False).to_pil()
    else: # page >= len(doc):
        image = doc[len(doc) - 1].render(scale=IMAGE_DPI / 72, draw_annots=False).to_pil()

    image = image.convert("RGB")
    bboxes = page_dict.get(page, None)
    if bboxes:
        for bbox in bboxes:
            draw = ImageDraw.Draw(image)
            bbox = enlarge_bbox(bbox)
            draw.rectangle(bbox, outline=(255, 0, 0), width=3)
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()
