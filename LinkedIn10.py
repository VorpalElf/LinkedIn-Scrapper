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
    await page.act("✅ type 'Data Analyst' into the search job titles or companies input. Then click the search button")
    await asyncio.sleep(30)
    await page.act(f"✅ click job listing number {i+1}")
    result = await page.extract("extract company, job titles, job description and company information")
    print("Raw extraction result:", result)
    await stagehand.close()
    return result

async def main():
    results = []
    for batch_start in range(0, 10, 2):
        tasks = [scrape_job(i) for i in range(batch_start, batch_start + 2)]
        batch_results = await asyncio.gather(*tasks)
        results.extend(batch_results)
        if batch_start + 2 < 10:
            print("Waiting 15 seconds before next pair...")
            await asyncio.sleep(15)
    with open('outputv5.md', 'w') as f:
        for idx, res in enumerate(results, 1):
            res_str = str(res).replace("\\n", "\n")
            f.write(f"\nJob {idx}:\n{res_str}\n")

if __name__ == "__main__":
    asyncio.run(main())