import asyncio
import os
from stagehand import Stagehand, StagehandConfig
from dotenv import load_dotenv

load_dotenv()

async def scrape_job(i):
    config = StagehandConfig(
        env="BROWSERBASE",
        api_key=os.getenv("BROWSERBASE_API_KEY"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        model_name="gpt-4o",
        model_api_key=os.getenv("MODEL_API_KEY"),
        proxies=True
    )
    stagehand = Stagehand(config)
    await stagehand.init()
    page = stagehand.page
    await page.goto("https://www.linkedin.com")
    await page.act("✅ click the Jobs button")
    await page.act("✅ click the X button to close the dialog")
    await page.act("✅ type 'Data Analyst' into the search job titles field")
    await asyncio.sleep(30)
    await page.act("click the search button")
    await page.act(f"✅ click job listing number {i+1}")
    result = await page.extract("extract job title, company, location, and full job description")
    await stagehand.close()
    return result

async def main():
    result = await scrape_job(0)
    result_str = str(result).replace("\\n", "\n")
    with open('output.md', 'w') as f:
        f.write(f"{result_str}\n")

if __name__ == "__main__":
    asyncio.run(main())