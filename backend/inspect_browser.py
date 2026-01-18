from browser_use import Browser
import asyncio

async def main():
    browser = Browser(headless=True)
    print("Attributes of BrowserSession:")
    for attr in dir(browser):
        if not attr.startswith("_"):
            print(attr)
    
if __name__ == "__main__":
    asyncio.run(main())
