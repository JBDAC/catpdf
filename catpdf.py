import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import argparse

def add_separator_page(output_pdf, page_number, docID, pdf_file):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    if docID != 0:
        separator_text = f"ID {docID} - Page {page_number} - {pdf_file}"
    else:
        separator_text = f"Page {page_number} - {pdf_file}"
        
    can.drawString(72, 40, separator_text)  # Change Y-coordinate to 40 for bottom-left corner
    can.save()
    packet.seek(0)
    separator_overlay = PyPDF2.PdfFileReader(packet)
    separator_page = separator_overlay.getPage(0)
    output_pdf.addPage(separator_page)

def add_page_with_name(output_pdf, pdf_file, page_number, index_file,  write_separator, docID, url_prefix=None):
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)

    if write_separator:
        # Output separator index entry to merged PDF
        add_separator_page(output_pdf, page_number, docID, pdf_file)    # Output separator index entry to merged PDF
    
    # Output index entry to index file as HTML with hyperlink
    if url_prefix:
        with open(index_file + ".html", 'a') as index_html:
            url = f"{url_prefix}{pdf_file}"  # Create hyperlink URL
            index_html.write('<tr><td style="text-align:left;"><a href="{}">{}</a></td><td>{}</td></tr>\n'.format(url, pdf_file, page_number))

    # Output index entry to index file as plain text
    with open(index_file + ".txt", 'a') as index_txt:
        if docID != 0:
            index_txt.write("ID {}\tPage {}\t{}\n".format(docID, page_number, pdf_file))
        else:
            index_txt.write("Page {}\t{}\n".format(page_number, pdf_file))

    # Merge the actual pages of the PDF and add page numbers
    for page_num in range(pdf_reader.getNumPages()):
        page = pdf_reader.getPage(page_num)
#        page.mergePage(create_page_number_overlay(page_number + page_num + 1))
        if write_separator:
            page_num += 1

        page.mergePage(create_page_number_overlay(docID, page_number + page_num))
        if not write_separator:
            page_num += 1

        output_pdf.addPage(page)

def create_page_number_overlay(docID, page_number):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    if docID != 0:
        text = f"ID {docID} - Page {page_number}"  # Use docID & page number
    else:
        text = f"Page {page_number}"  # Use only page number

    can.drawString(72, 40, text)  # Change Y-coordinate to 40 for bottom-left corner
    can.save()
    packet.seek(0)
    overlay = PyPDF2.PdfFileReader(packet)
    return overlay.getPage(0)

def merge_pdfs(pdf_list, output_filename, index_file,  write_separator, document_id, url_prefix=None):
    output_pdf = PyPDF2.PdfFileWriter()
    page_number = 1  # Track the current page number
    docID = 0	#Number the docs sequentially

    with open(pdf_list, 'r') as file:
        for line in file:
            pdf_file = line.strip()

            if document_id:
                if pdf_file != "BlankPage.pdf":
                    docID += 1

            add_page_with_name(output_pdf, pdf_file, page_number, index_file, write_separator, docID, url_prefix)
            print(pdf_file)
            pdf_reader = PyPDF2.PdfFileReader(pdf_file)
            num_pages = pdf_reader.getNumPages()
            # Increment the page number by the number of pages in the PDF plus one for the separator index entry
            if write_separator:
                num_pages += 1

            page_number += num_pages 


    with open(output_filename, 'wb') as output_file:
        output_pdf.write(output_file)


def convert_index_to_pdf(index_file, start_page_number, entries_per_page=35):
    # Use a smaller font
    font_name = "Helvetica"
    font_size = 10

    if not index_file.endswith(".txt"):
        index_file += ".txt"

    output_pdf = PyPDF2.PdfFileWriter()
    index = 0
    output_stream = io.BytesIO()  # Initialize the output_stream and output_canvas before the loop
    output_canvas = canvas.Canvas(output_stream, pagesize=letter)
    output_canvas.setFont("Helvetica", 12)

    with open(index_file, 'r') as index_txt:  # Use the updated index_file with ".txt" extension
        for line in index_txt:
            index += 1
            if index > entries_per_page:
                index = 1
                output_canvas.save()
                output_stream.seek(0)
                overlay = PyPDF2.PdfFileReader(output_stream)
                current_page = overlay.getPage(0)
                output_pdf.addPage(current_page)

                output_stream = io.BytesIO()  # Reset the output_stream and output_canvas
                output_canvas = canvas.Canvas(output_stream, pagesize=letter)
                output_canvas.setFont("Helvetica", 12)

            entry = line.strip().replace('\t', '    ')  # Replace tab characters with 4 spaces
            output_canvas.drawString(72, 750 - (index * 20), entry)
            start_page_number += 1

    # Add the last page
    if index > 0:
        output_canvas.save()
        output_stream.seek(0)
        overlay = PyPDF2.PdfFileReader(output_stream)
        current_page = overlay.getPage(0)
        output_pdf.addPage(current_page)

    with open(f"{index_file[:-4]}.pdf", 'wb') as output_pdf_file:
        output_pdf.write(output_pdf_file)

def main():
    parser = argparse.ArgumentParser(description='Merge PDFs and add page numbers with separator index.')
    parser.add_argument('pdf_list', help='Path to the text file containing the list of PDFs to merge')
    parser.add_argument('output_filename', help='Path to the output merged PDF file')
    parser.add_argument('index_file', help='Name for the index file (without extension)')
    parser.add_argument('-e', '--entries-per-page', type=int, default=35, help='Number of entries per page in the index.pdf file (default is 35)')
    parser.add_argument('-u', '--url-prefix', help='URL prefix for hyperlinks in the index.html file')
    parser.add_argument('-a', '--append-index', action='store_true', help='Append the index.pdf file to the merged PDF if provided')
    parser.add_argument('-s', '--separator', action='store_true', help='Do write separator pages to the merged PDF')
    parser.add_argument('-d', '--document-id', action='store_true', help='Sequential Document number ID')

    args = parser.parse_args()
    print("Merge PDFs. © James Collings 2023. Ver 2023.08.03")
    print("By using this software, you accept and agree that its use is at your own risk. The author assumes no liability for any damages or issues arising from its use.")
    
    proceed = input("Proceed with PDF merging? (Yes/No): ").lower()
    if proceed not in ['y', 'yes']:
        print("PDF merging canceled.")
        return

    with open(args.index_file + ".html", 'w') as index_html:
        index_html.write('<!DOCTYPE html>\n<html>\n<body>\n<table>\n<tr><th style="text-align:left;">Filename/Link</th><th>Page Number</th></tr>\n')
    with open(args.index_file + ".txt", 'w'):
        pass

    merge_pdfs(args.pdf_list, args.output_filename, args.index_file, args.separator, args.document_id, args.url_prefix)
    convert_index_to_pdf(args.index_file, start_page_number=1, entries_per_page=args.entries_per_page)

    with open(args.index_file + ".html", 'a') as index_html:
        index_html.write('</table>\n</body>\n</html>\n')

    if args.append_index:
        # Merge the index PDF with the merged PDF
        with open(args.index_file + ".pdf", 'rb') as index_pdf_file:
            with open(args.output_filename, 'rb') as merged_pdf_file:
                output_pdf = PyPDF2.PdfMerger()
                output_pdf.append(merged_pdf_file)

                index_pdf = PyPDF2.PdfFileReader(index_pdf_file)
                output_pdf.merge(len(output_pdf.pages), index_pdf)

                # Write the final merged PDF with the index.pdf appended to disk
                with open(args.output_filename, 'wb') as output_file:
                    output_pdf.write(output_file)

    print("PDFs merged successfully!")

if __name__ == "__main__":
    main()
