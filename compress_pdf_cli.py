import argparse
from pdf_compressor import PDFCompressor

def main():
    parser = argparse.ArgumentParser(description='Compress PDF files')
    parser.add_argument('input', help='Input PDF file path')
    parser.add_argument('output', help='Output PDF file path')
    parser.add_argument('-q', '--quality', type=int, default=30,
                        help='Compression quality (0-100, default: 30)')

    args = parser.parse_args()

    compressor = PDFCompressor()
    success = compressor.compress_pdf(args.input, args.output, args.quality)

    if success:
        print("PDF compression completed successfully!")
    else:
        print("PDF compression failed!")

if __name__ == "__main__":
    main() 