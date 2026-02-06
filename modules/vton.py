import io
import time
from PIL import Image
import streamlit as st

from google import genai
from google.genai import types

def get_gemini_client():
    """Get Gemini client using API key from session state."""
    api_key = st.session_state.get('gemini_api_key')
    if not api_key:
        raise ValueError("Gemini API key not found. Please enter it in the sidebar.")
    return genai.Client(api_key=api_key)

def get_vton_model():
    """Get the selected VTON model from session state."""
    return st.session_state.get('vton_model', 'gemini-2.0-flash-preview-image-generation')

def _load_pil_image_as_part(pil_image: Image.Image, filename_hint: str) -> types.Part:
    """
    Helper to convert a PIL Image directly into a Gemini API Part object
    without saving it to disk first.
    """
    # Convert PIL image to byte buffer in memory
    buf = io.BytesIO()
    # Use the format derived from the filename hint (e.g., 'person.jpg' -> 'JPEG')
    img_format = 'PNG' if filename_hint.lower().endswith('.png') else 'JPEG'
    # Save using high quality
    pil_image.save(buf, format=img_format, quality=95)
    byte_data = buf.getvalue()
    
    # Determine mime type based on the format we just used
    mime_type = f"image/{img_format.lower()}"

    return types.Part(
        inline_data=types.Blob(
            data=byte_data,
            mime_type=mime_type
        )
    )

def process_virtual_tryon(person_img_pil: Image.Image, garment_img_pil: Image.Image):
    """
    Generates a Virtual Try-On image using Google Gemini's image generation model.
    """
    model_name = get_vton_model()
    print(f"\n--- VTON: Starting Image Generation ({model_name}) ---")
    
    start_time = time.time()

    try:
        client = get_gemini_client()

        # Prepare the contents list for the API call
        contents = []
        
        # Load images using our in-memory helper
        contents.append(_load_pil_image_as_part(person_img_pil, "person.png"))
        contents.append(_load_pil_image_as_part(garment_img_pil, "garment.png"))
        
        # Add the text prompt defining the VTON task
        vton_prompt = (
            "Generate a virtual try-on image. "
            "Take the person from the first image and show them wearing the garment from the second image. "
            "Keep the person's face, body pose, and background the same. "
            "Only replace their clothing with the garment shown."
        )
        contents.append(types.Part.from_text(text=vton_prompt))

        print(f"Sending request to Gemini model {model_name}...")
        st.toast("Sending request to Gemini...", icon="✨")

        # Configuration for image generation
        config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        )

        # Call the generate_content API
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config,
        )

        end_time = time.time()
        print(f"Generation complete in {end_time - start_time:.2f}s.")

        # Process the response - look for image data
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    # Extract the raw image bytes
                    raw_image_bytes = part.inline_data.data
                    
                    # Convert raw bytes back to a PIL Image for Streamlit
                    generated_img = Image.open(io.BytesIO(raw_image_bytes))
                    
                    st.toast("Image Generation Complete!", icon="✨")
                    return generated_img
        
        # If no image found, check for text response
        if response.text:
            raise Exception(f"Model returned text instead of image: {response.text[:200]}")
        else:
            raise Exception("API response did not contain valid image data.")

    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ VTON Error: {error_msg}")
        st.error(f"An error occurred during image generation: {error_msg}")
        return person_img_pil
