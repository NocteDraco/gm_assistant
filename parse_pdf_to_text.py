import argparse
import pypdfium2 as pdfium
import re
import os



"""
TODO ALL OF THIS
"""

def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--page_offset", type = int, default = 0)
    parser.add_argument("--page_steps", type = int, default = 60)
    parser.add_argument("--output_dir", type = str, default = '.')
    return parser



def main(args):
    pdf = pdfium.PdfDocument(args.file)
    all_pages = [q.get_textpage().get_text_range().replace("\n", " ").replace("\r", "\n") for q in pdf]
    


if __name__ == '__main__':
    parser = build_parser()

    args = parser.parse_args()

    main(args)