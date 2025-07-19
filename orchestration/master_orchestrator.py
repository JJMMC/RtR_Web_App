from orchestration.data_orchestrator
from


class MasterOrchestrator:
    def __init__(self):
        self.scrap_orch = ScrapOrchestrator()
        self.data_orch = DataOrchestrator()
        self.db_orch = DatabaseOrchestrator()
    
    async def run_complete_pipeline(self):
        # 1. Scraping
        scraped_data = await self.scrap_orch.run_full_scraping()
        # 2. Guardar temporal
        await self.data_orch.save_to_temp_files(scraped_data)
        # 3. Insert a DB
        await self.db_orch.insert_scraped_data(scraped_data)
        # 4. Update analytics
        await self.db_orch.update_analytics()