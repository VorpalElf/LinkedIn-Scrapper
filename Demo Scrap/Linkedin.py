import asyncio
import os
from stagehand import Stagehand, StagehandConfig
from dotenv import load_dotenv
from IPython.display import Markdown

load_dotenv()

async def main():
    config = StagehandConfig(
        env="BROWSERBASE",
        api_key=os.getenv("BROWSERBASE_API_KEY"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        model_name="gpt-4o",
        model_api_key=os.getenv("MODEL_API_KEY")
    )
    
    stagehand = Stagehand(config)
    
    try:
        await stagehand.init()
        page = stagehand.page
        
        await page.goto("https://www.linkedin.com")
        print("Navigated")
        
        await page.act("✅ click the Jobs button")
        print("Jobs clicked")
        
        await page.act("✅ click the X button to close the dialog")
        print("Login bye")
        
        await page.act("✅ type 'Data Analyst' into the search job titles or companies input")
        print("Field typed")
        
        await page.act("✅ click the search button")
        print("Searching")
        
        result = await page.extract("extract the top 10 Data Analyst job listings with company name, location")
        
        with open('output.md', 'w') as f:
            result = str(result).replace("extraction='", "").replace("\\n", "\n")
            f.write(result)
        
    finally:
        await stagehand.close()
        
        
if __name__ == "__main__":
    asyncio.run(main())    