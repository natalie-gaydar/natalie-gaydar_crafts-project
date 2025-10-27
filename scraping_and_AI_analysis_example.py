# scrapes text content from a webpage using Playwright
# assumes you'fe installed Playwright and the Chromium browser:
# pip install playwright
# python -m playwright install chromium 
import time
from playwright.sync_api import sync_playwright  
import re

def auto_scroll(page, iterations=12, pause=0.75):
    """Scroll to the bottom repeatedly to trigger lazy-loaded content."""
    last_h = 0

    for i in range(iterations):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(pause)
        print(".", end="", flush=True)  # Print dot for each scroll
        h = page.evaluate("document.body.scrollHeight")
        if h == last_h:
            print(f" Done!)")
            break
        last_h = h
    else:
        print(" Done!")  # If we completed all iterations

def scrape_URL_for_text(url):
    # Hardcoded arguments (edit these values instead of parsing CLI args)

    timeout = 60000  # milliseconds
    print("Loading page content", end="", flush=True)  # Start the progress line
    with sync_playwright() as p:
        # Run Playwright locally (no BrowserCat / no wss)
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 900},
        )
        page = context.new_page()

        # Speed: skip heavy assets that aren't needed for text/HTML extraction
        context.route("**/*", lambda route: route.abort()
                      if route.request.resource_type in {"image", "media", "font"}
                      else route.continue_())

        # Navigate and wait for the page to quiet down
        page.goto(url, wait_until="networkidle", timeout=timeout)

        # Try to dismiss any cookie banner (best-effort; ignore errors)
        for selector in [
            "button:has-text('Accept')",
            "button:has-text('I Agree')",
            "text=/accept all cookies/i",
        ]:
            try:
                page.locator(selector).first.click(timeout=2000)
                break
            except Exception:
                pass

        # Trigger lazy-loaded content
        auto_scroll(page)

        # 1) Fully rendered HTML (serialized DOM).  <-- "true" HTML after JS runs
        rendered_html = page.content()

        # 2) Readable text (tags stripped) - try to target the main article first
        selectors = ['article', 'main', '[role=main]', '[itemprop=articleBody]', '.article', '.post', '.entry-content', '.content']
        readable_text = ""
        for s in selectors:
            try:
                el = page.query_selector(s)
                if el:
                    # Remove all anchor tags from this element before getting text
                    page.evaluate(f"""
                        document.querySelectorAll('{s} a').forEach(a => a.remove());
                    """)
                    txt = (el.inner_text() or "").strip()
                    if len(txt) > 100:
                        readable_text = re.sub(r'\n{3,}', '\n\n', txt).strip()
                        break
            except Exception:
                pass

        if not readable_text:
            # Fallback: clone body and remove likely non-article regions (header/footer/nav/aside/sidebar)
            readable_text = page.evaluate(
                """() => {
                    const clone = document.body.cloneNode(true);
                    const removeSel = ['header','footer','nav','aside','[class*="sidebar"]','[class*="cookie"]','[class*="masthead"]','a'];
                    removeSel.forEach(sel => {
                        clone.querySelectorAll(sel).forEach(n => n.remove());
                    });
                    return (clone.innerText || '').replace(/\\n{3,}/g, '\\n\\n').trim();
                }"""
            )

        # Print to stdout
        #print("\n=== RENDERED HTML ===\n")
        #print(rendered_html)
        #print("\n=== READABLE TEXT ===\n")
        #print(readable_text)

        fname = "data\\" + url.split("/")[-2] + ".txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(readable_text)

        browser.close()

        return readable_text

#URL = input("Url from instructables: ")
text_content = scrape_URL_for_text("https://www.instructables.com/How-to-make-an-awesome-pencil-sketch-of-any-photog/")
print(f"Scraped text content from https://www.instructables.com/How-to-make-an-awesome-pencil-sketch-of-any-photog/:\n" + text_content)

input()

#
# Process text with AI to extract materials and instructions
#

from openai import OpenAI
from keys import OPENAI_API_KEY

def extract_materials_and_instructions(text_content, project_title=""):

    
    # Initialize OpenAI client (make sure to set your API key)
    client = OpenAI(
        api_key=OPENAI_API_KEY  # Set this environment variable
    )
    
    prompt = f"""
    Please analyze the following craft project text and extract the materials and step-by-step instructions.
    
    Format your response as plain text with these two sections:
    
    MATERIALS:
    - List each material needed (one per line with dashes)
    
    INSTRUCTIONS:
    1. List each step numbered (clear, concise steps)
    
    Keep the language clear and concise. Remove any website navigation text, ads, or irrelevant content.
    Only include the essential materials and steps for completing the craft project.
    
    Project text:
    {text_content}
    """
    
    try:
        print("Analyzing text with OpenAI...", end="", flush=True)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts craft project information. Respond with clean, plain text formatting."},
                {"role": "user", "content": prompt}
            ],
            #max_tokens=2000,
            temperature=0.0  # Lower temperature for more consistent extraction
        )
        
        print(" Done!")
        
        # Return the text response directly as a string
        result = response.choices[0].message.content.strip()
        return result
            
    except Exception as e:
        print(f"\nError with OpenAI API: {e}")
        return f"ERROR: {e}"


instructions = extract_materials_and_instructions(text_content)
print(instructions)