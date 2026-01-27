from pathlib import Path
from adp.services.observer.base_observer import BaseObserver
from adp.configs.logger import worker_logger as logger
from adp.configs.settings import settings

class LocalTarget(BaseObserver):
    def __init__(self):
        self.local_dir = Path(settings.LOCAL_SAVED_DIR)
        self.local_dir.mkdir(parents=True, exist_ok=True)

    async def update(self, data: str, file_name: str, *args, **kwargs) -> str:
        """
        Save data as a markdown file locally.
        """
        clean_name = Path(file_name).with_suffix('.md')
        output_path = self.local_dir / clean_name

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(data)
        logger.info(f"[Observer] Saved to Local: {output_path}")
        return str(output_path)

    async def close(self):
        pass
