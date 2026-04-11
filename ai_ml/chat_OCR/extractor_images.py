# extractor_images.py
import fitz
import os

def extract_images_from_pdf(pdf_path: str, output_dir: str):
    """
    Extracts embedded images from a PDF using PyMuPDF.
    Saves them as PNG files.
    """
    os.makedirs(output_dir, exist_ok=True)

    try:
        doc = fitz.open(pdf_path)
        image_paths = []

        for page_num, page in enumerate(doc):
            image_list = page.get_images(full=True)

            for img_index, img_info in enumerate(image_list):
                xref = img_info[0]
                base_image = doc.extract_image(xref)

                img_bytes = base_image["image"]
                img_ext = base_image["ext"]
                img_path = os.path.join(output_dir, f"page_{page_num+1}_img_{img_index+1}.{img_ext}")

                with open(img_path, "wb") as img_file:
                    img_file.write(img_bytes)

                image_paths.append(img_path)

        doc.close()
        return image_paths

    except Exception as e:
        raise RuntimeError(f"Error extracting images: {e}")
