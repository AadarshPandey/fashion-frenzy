import asyncio
import json
import nest_asyncio
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import streamlit as st

# --- Apply nest_asyncio for Jupyter/Streamlit compatibility ---
nest_asyncio.apply()

# --- Data Schemas ---
class ProductItem(BaseModel):
    product_name: str = Field(..., description="The full name of the product.")
    actual_price: str = Field(..., description="Original price. Use 'N/A' if missing.")
    offer_price: str = Field(..., description="Discounted selling price.")
    rating: str = Field(..., description="Product rating (e.g., '4.5 out of 5 stars'). Use 'N/A' if missing.")
    image_link: str = Field(..., description="Full absolute URL of the product image starting with https://")
    product_link: str = Field(..., description="Full absolute URL to the product page starting with https://www.amazon.in/. If relative URL found like /dp/XXX, prepend https://www.amazon.in")
    occasion_fit: str = Field(default="", description="Brief explanation of how this product fits the occasion (e.g., 'Perfect for weddings', 'Great for formal events').")

class ProductList(BaseModel):
    products: List[ProductItem] = Field(..., description="List of products found.")

async def scrape_product_async(product_name: str, record_count: int = 5) -> List[Dict[str, Any]]:
    """
    Scrapes Amazon for products using crawl4ai with Gemini for extraction.
    """
    print(f"🕵️ SCRAPER: Starting search for '{product_name}' (Target: {record_count} items)...")
    
    # Get API key from session state
    api_key = st.session_state.get('gemini_api_key', '')
    if not api_key:
        print("❌ SCRAPER: No API key found in session state")
        return []
    
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
        from crawl4ai.extraction_strategy import LLMExtractionStrategy
        from crawl4ai.async_configs import LLMConfig
    except ImportError:
        print("❌ SCRAPER: crawl4ai not installed. Returning empty results.")
        return []
    
    url = f"https://www.amazon.in/s?k={product_name.replace(' ', '+')}"
    
    # Configure Gemini for extraction - NOTE: litellm uses "gemini/" prefix
    llm_config = LLMConfig(
        provider="gemini/gemini-2.0-flash",
        api_token=api_key
    )

    llm_strategy = LLMExtractionStrategy(
        llm_config=llm_config,
        schema=ProductList.model_json_schema(),
        extraction_type="schema",
        instruction=(
            f"Extract valid products with their names, prices, ratings, images, and links. "
            f"Ignore sponsored ads. Return at least {record_count} items. "
            "CRITICAL FOR LINKS: "
            "- For product_link: Extract the FULL absolute URL starting with https://www.amazon.in/. "
            "  If you find a relative URL like '/dp/B0XXX...' or '/gp/...', prepend 'https://www.amazon.in' to make it absolute. "
            "- For image_link: Extract the FULL image URL starting with https://. "
            "For each product, also provide an 'occasion_fit' field explaining how well the product suits the searched occasion."
        ),
        chunk_token_threshold=2000,
        overlap_rate=0.1
    )

    browser_config = BrowserConfig(
        headless=True, 
        verbose=False, 
        user_agent_mode="random"
    )

    # Scroll script to load lazy-loaded content
    scroll_script = """
        window.scrollTo(0, document.body.scrollHeight / 2);
        await new Promise(r => setTimeout(r, 1000));
        window.scrollTo(0, document.body.scrollHeight);
        await new Promise(r => setTimeout(r, 1000));
    """

    run_config = CrawlerRunConfig(
        extraction_strategy=llm_strategy,
        cache_mode=CacheMode.BYPASS,
        wait_for="css:.s-main-slot", 
        js_code=scroll_script,
        magic=True,
        page_timeout=30000
    )

    all_products = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        print(f"🚀 SCRAPER: Crawling {url}")
        try:
            result = await crawler.arun(url=url, config=run_config)
            
            if result.success and result.extracted_content:
                data = json.loads(result.extracted_content)
                
                products_found = []
                if isinstance(data, dict) and "products" in data:
                    products_found = data["products"]
                elif isinstance(data, list):
                    products_found = data
                
                if products_found:
                    print(f"✅ SCRAPER: Found {len(products_found)} items")
                    all_products.extend(products_found[:record_count])
                else:
                    print(f"⚠️ SCRAPER: Content extracted but no products found.")
            else:
                print(f"❌ SCRAPER: Failed to extract content. Error: {result.error_message}")
                
        except Exception as e:
            print(f"⚠️ SCRAPER CRASH: {str(e)}")

    return all_products

def run_scraper_tool(product_name: str, record_count: int = 5) -> List[Dict[str, Any]]:
    """
    Synchronous wrapper that safely calls the async scraper.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create a new loop in a thread for Streamlit compatibility
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    lambda: asyncio.run(scrape_product_async(product_name, record_count))
                )
                return future.result(timeout=60)
        else:
            return asyncio.run(scrape_product_async(product_name, record_count))
    except Exception as e:
        print(f"⚠️ SCRAPER ERROR: {str(e)}")
        return []

if __name__ == "__main__":
    # Test run
    test_product = "mechanical keyboard"
    results = run_scraper_tool(test_product, 5)
    print(json.dumps(results, indent=2))
    print(f"Total records retrieved: {len(results)}")