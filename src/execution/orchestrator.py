from src.app.generic_bot_app import GenericBotApplication
from src.utilities.logger import Logger
import logging
from src.utilities.utils import load_config


class ExecutionOrchestrator:

    @staticmethod
    def run(config_path: str) -> None:
        Logger()
        cfg = load_config(config_path)

        try:
            app = GenericBotApplication()
            app.execute(cfg)

        except Exception as err:
            logging.error(f"Error in ExecutionOrchestrator: {err}")
            raise
            

