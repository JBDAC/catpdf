python catpdf.py -h

usage: catpdf.py [-h] [-e ENTRIES_PER_PAGE] [-u URL_PREFIX] [-a] [-s] [-d]
                 pdf_list output_filename index_file

Merge PDFs and add page numbers with separator index.

positional arguments:
  pdf_list              Path to the text file containing the list of PDFs to
                        merge
  output_filename       Path to the output merged PDF file
  index_file            Name for the index file (without extension)

options:
  -h, --help            show this help message and exit
  -e ENTRIES_PER_PAGE, --entries-per-page ENTRIES_PER_PAGE
                        Number of entries per page in the index.pdf file
                        (default is 35)
  -u URL_PREFIX, --url-prefix URL_PREFIX
                        URL prefix for hyperlinks in the index.html file
  -a, --append-index    Append the index.pdf file to the merged PDF if
                        provided
  -s, --separator       Do write separator pages to the merged PDF
  -d, --document-id     Sequential Document number ID
