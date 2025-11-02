import os
from google import genai
from google.genai import types
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

def get_llm_response(context: str, query: str) -> str:
    """
    Send a user query and context to Google Gemini and return the assistant's response.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set. "
            "Please set it to your Google Gemini API key."
        )

    # Initialize Gemini client
    client = genai.Client(api_key=api_key)
    model = "gemini-2.0-flash"

    # Build content
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=f"""
Document text:
{context}

User question:
{query}
"""
                )
            ],
        ),
    ]

    # Set generation config
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(
                text=(
                    """
                    You are an intelligent PDF assistant. 
                    Answer questions strictly based on the provided document text.

                    ### Rules:
                    1. Use only information from the document.
                    2. If the answer isn't present, say exactly:
                       "Sorry, the answer is not available in the document."
                    3. Keep your answers concise and factual.
                    4. If the document is technical, include examples or formulas.
                    5. Never assume or hallucinate extra details.
                    """
                )
            )
        ],
    )

    # Stream and collect response
    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model, contents=contents, config=generate_content_config
    ):
        if chunk.text:
            response_text += chunk.text

    return response_text.strip()
