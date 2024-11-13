import os
import fitz  # PyMuPDF
from PIL import Image
import io
import tempfile
from PyPDF2 import PdfReader, PdfWriter
import img2pdf

class PDFCompressor:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()

    def compress_pdf(self, input_path, output_path, quality=30):
        """
        Compress PDF file with customizable quality
        
        Args:
            input_path (str): Path to input PDF file
            output_path (str): Path to save compressed PDF
            quality (int): Compression quality (0-100, lower means more compression)
        """
        try:
            # Open the PDF with PyMuPDF
            pdf_document = fitz.open(input_path)
            pdf_writer = PdfWriter()

            # Adjust quality parameters for better balance
            target_dpi = int(150 * (quality / 30))  # Increased base DPI to 150
            image_quality = min(max(quality * 2, 40), 80)  # Keep quality between 40-80

            for page_num in range(pdf_document.page_count):
                print(f"Processing page {page_num + 1}/{pdf_document.page_count}")
                page = pdf_document[page_num]
                
                # Create a new PDF page with higher resolution
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))  # Increased resolution
                
                # Convert to PIL Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Compress the image
                img = self._compress_image(img, quality=quality)
                
                # Save as temporary JPEG with better quality
                temp_img_path = os.path.join(self.temp_dir, f"temp_{page_num}.jpg")
                img.save(temp_img_path, 'JPEG', quality=image_quality, optimize=True)
                
                # Convert JPEG to PDF using img2pdf
                temp_pdf_path = os.path.join(self.temp_dir, f"temp_{page_num}.pdf")
                with open(temp_img_path, "rb") as image_file:
                    pdf_bytes = img2pdf.convert(image_file)
                    with open(temp_pdf_path, "wb") as pdf_file:
                        pdf_file.write(pdf_bytes)
                
                # Add the compressed page to the output PDF
                temp_reader = PdfReader(temp_pdf_path)
                pdf_writer.add_page(temp_reader.pages[0])
                
                # Clean up temporary files
                os.remove(temp_img_path)
                os.remove(temp_pdf_path)

            # Save the compressed PDF
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)

            # Clean up
            pdf_document.close()
            
            # Get file sizes
            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(output_path)
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            print(f"Original Size: {self._format_size(original_size)}")
            print(f"Compressed Size: {self._format_size(compressed_size)}")
            print(f"Compression Ratio: {compression_ratio:.2f}%")
            
            return True

        except Exception as e:
            print(f"Error compressing PDF: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _compress_image(self, image, quality=30):
        """Compress image with various techniques"""
        # Calculate new size based on quality - more conservative scaling
        scale_factor = max(quality / 60, 0.5)  # Minimum scale is 50%
        new_width = int(image.width * scale_factor)
        new_height = int(image.height * scale_factor)
        
        # Increased minimum dimensions for better quality
        new_width = max(new_width, 1200)  # Increased from 800
        new_height = max(new_height, int(1200 * (image.height / image.width)))
        
        # Resize image with high-quality resampling
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        return image

    def _format_size(self, size):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

def main():
    # Example usage
    compressor = PDFCompressor()
    
    input_file = "input.pdf"
    output_file = "compressed_output.pdf"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        return
    
    print("Starting PDF compression...")
    success = compressor.compress_pdf(input_file, output_file)
    
    if success:
        print("PDF compression completed successfully!")
    else:
        print("PDF compression failed!")

if __name__ == "__main__":
    main() 