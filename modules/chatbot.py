import json
import streamlit as st
from google import genai
from google.genai import types

# Import the scraper from your module
from modules.ecommerce_scraper import run_scraper_tool

def get_gemini_client():
    """Get Gemini client using API key from session state."""
    api_key = st.session_state.get('gemini_api_key')
    if not api_key:
        raise ValueError("Gemini API key not found. Please enter it in the sidebar.")
    return genai.Client(api_key=api_key)

def get_chat_model():
    """Get the selected chat model from session state."""
    return st.session_state.get('chat_model', 'gemini-2.0-flash')

# --- Tool/Function Definitions for Gemini ---
SCRAPER_TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="search_products",
            description="Searches for products on Amazon/E-commerce sites. Use this when the user specifically wants to buy, find, or search for a new item to add to their wardrobe.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "product_name": types.Schema(
                        type=types.Type.STRING,
                        description="The search keywords for the product (e.g., 'beige chinos men', 'floral summer dress')."
                    ),
                    "record_count": types.Schema(
                        type=types.Type.INTEGER,
                        description="Number of products to retrieve. Default is 5."
                    )
                },
                required=["product_name"]
            )
        )
    ]
)

def chat_with_gemini(user_input: str, history: list, wardrobe_context: str) -> str:
    """
    Chat function using Google Gemini:
    1. Sends context + user prompt to Gemini.
    2. Checks if Gemini wants to use the 'search_products' tool.
    3. If yes, executes the scraper, gets results, and sends them back.
    4. Returns the final natural language response.
    """
    try:
        client = get_gemini_client()
        model_name = get_chat_model()
        # Get user gender preference
        user_gender = st.session_state.get('user_gender', 'Male')
        
        # System instruction with wardrobe and gender context
        system_instruction = (
            f"You are an intelligent personalized wardrobe curator and shopping companion for a {user_gender.upper()} user. "
            "You are helpful, stylish, and friendly. "
            f"IMPORTANT: The user is {user_gender}. Always search for and recommend {user_gender.lower()}'s clothing/fashion items. "
            "You have access to the user's existing wardrobe (listed below) to suggest outfits. "
            "You ALSO have a tool to search for new products online. "
            f"When searching, always include '{user_gender.lower()}' or 'men' or 'women' appropriately in the search query. "
            "If the user asks to buy something or needs a specific item to complete an outfit, use the 'search_products' tool.\n\n"
            
            "CRITICAL: When displaying product results, you MUST format each product as a beautiful card using HTML for images:\n\n"
            
            "---\n"
            "### 🛍️ [Product Name]\n\n"
            '<img src="IMAGE_URL_HERE" alt="Product" width="200" style="border-radius: 10px; margin: 10px 0;">\n\n'
            "| Detail | Info |\n"
            "|--------|------|\n"
            "| 💰 **Price** | ~~₹Original~~ **₹Offer Price** |\n"
            "| ⭐ **Rating** | 4.5/5 stars |\n"
            "| 🎯 **Why it's perfect** | [Occasion fit explanation] |\n\n"
            "🔗 [**Buy Now →**](product_link)\n\n"
            "---\n\n"
            
            "FORMATTING RULES:\n"
            "1. Start with a brief intro like 'Here are some perfect options for your friend's wedding!'\n"
            "2. Show EACH product as a separate card with the format above\n"
            "3. Use the table format for structured details\n"
            '4. CRITICAL: Display images using HTML: <img src="URL" alt="Product" width="200">\n'
            "5. Make the 'Buy Now' link clickable using markdown: [Buy Now](url)\n"
            "6. Add a brief personal recommendation at the end\n"
            "7. If prices have discounts, show original price struck through (~~₹X~~)\n"
            "8. Use the occasion_fit field to explain why this product suits the event\n\n"
            
            f"USER GENDER: {user_gender}\n"
            f"USER WARDROBE CONTEXT:\n{wardrobe_context}"
        )
        
        # Build conversation history for Gemini
        contents = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])]
            ))
        
        # Add current user message
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_input)]
        ))
        
        # Generate config
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[SCRAPER_TOOL],
            temperature=0.7
        )
        
        # First API call
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config
        )
        
        # Check if there are function calls
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    func_call = part.function_call
                    
                    if func_call.name == "search_products":
                        # Extract arguments
                        product_name = func_call.args.get("product_name", "")
                        record_count = func_call.args.get("record_count", 5)
                        
                        print(f"🤖 Gemini requested tool: Searching for '{product_name}'...")
                        
                        # Execute the scraper
                        tool_result = run_scraper_tool(product_name, record_count)
                        
                        # Add function call and result to conversation
                        contents.append(types.Content(
                            role="model",
                            parts=[types.Part.from_function_call(
                                name=func_call.name,
                                args=dict(func_call.args)
                            )]
                        ))
                        
                        contents.append(types.Content(
                            role="user",
                            parts=[types.Part.from_function_response(
                                name=func_call.name,
                                response={"result": tool_result}
                            )]
                        ))
                        
                        # Second API call to process tool results
                        final_response = client.models.generate_content(
                            model=model_name,
                            contents=contents,
                            config=types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                temperature=0.7
                            )
                        )
                        
                        return final_response.text
        
        # No function call, return text response
        return response.text
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ CHATBOT ERROR: {error_msg}")
        return f"Error connecting to Gemini: {error_msg}"

def run_chat_tool(user_input: str, history: list, wardrobe_context: str) -> str:
    """
    Synchronous wrapper for chat_with_gemini.
    """
    return chat_with_gemini(user_input, history, wardrobe_context)