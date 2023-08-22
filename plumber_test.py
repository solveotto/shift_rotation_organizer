import pdfplumber

def combine_close_texts(text_objects, y_tolerance=1):
    """
    Combine text fragments that are close together vertically.
    """
    combined_texts = []
    current_text = text_objects[0]['text']
    current_bottom = text_objects[0]['bottom']
    
    for obj in text_objects[1:]:
        print(obj["text"])
        if abs(obj['top'] - current_bottom) < y_tolerance:
            current_text += obj['text']
            current_bottom = obj['bottom']
        else:
            combined_texts.append(current_text)
            current_text = obj['text']
            current_bottom = obj['bottom']
    
    combined_texts.append(current_text)
    return combined_texts

pdf = pdfplumber.open("turnus.pdf")
page = pdf.pages[0]

# Extract text objects with bounding boxes
text_objects = page.extract_words()

# Combine close text fragments
combined_texts = combine_close_texts(text_objects)

# Process combined text fragments to extract times, etc.
# ... rest of your processing code



pdf.close()


