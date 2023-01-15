import argparse
from pypdf import PdfReader
from pathlib import Path
import requests

PAPER_LOC = "./papers"
ARXIV_DOWNLOAD_URL = "http://export.arxiv.org/pdf"


def download_paper(url):
  print("Downloading paper")
  filename = url.split("/")[-1]
  filepath = Path(f"{PAPER_LOC}/{filename}")
  if not filepath.is_file():
    response = requests.get(url)
    filepath.write_bytes(response.content)
    print("Downloaded!")
  else:
    print("Paper already exists!")
    print("\n")
  return str(filepath)


def parse_paper(path):
  print("Parsing paper")
  reader = PdfReader(path)
  number_of_pages = len(reader.pages)
  print(f"Total number of pages: {number_of_pages}")
  paper_text = []
  for i in range(number_of_pages):
    page = reader.pages[i]
    page_text = []

    def visitor_body(text, cm, tm, fontDict, fontSize):
      x = tm[4]
      y = tm[5]
      # ignore header/footer
      if (y > 50 and y < 720) and (len(text.strip()) > 1):
        page_text.append({
          'fontsize': fontSize,
          'text': text.strip().replace('\x03', ''),
          'x': x,
          'y': y
        })

    _ = page.extract_text(visitor_text=visitor_body)

    blob_font_size = None
    blob_text = ''
    processed_text = []

    for t in page_text:
      if t['fontsize'] == blob_font_size:
        blob_text += f" {t['text']}"
      else:
        if blob_font_size is not None and len(blob_text) > 1:
          processed_text.append({
            'fontsize': blob_font_size,
            'text': blob_text,
            'page': i
          })
        blob_font_size = t['fontsize']
        blob_text = t['text']
    paper_text += processed_text
  return paper_text


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--arxiv-id", help="Use the arxiv id of the paper")
  parser.add_argument("--pdf-url", help="URL to the pdf of the paper")
  args = parser.parse_args()

  url = None
  if args.arxiv_id:
    url = f"{ARXIV_DOWNLOAD_URL}/{args.arxiv_id}.pdf"
  else:
    url = args.pdf_url

  if url is None:
    raise Exception("Paper not specified!")
  else:
    print("\n")
    Path(PAPER_LOC).mkdir(parents=True, exist_ok=True)
    filepath = download_paper(url)
    paper_contents = parse_paper(filepath)

  print(paper_contents)
