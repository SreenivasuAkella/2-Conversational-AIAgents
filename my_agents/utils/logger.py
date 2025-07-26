import logging
import os

def setup_logger():
    os.makedirs("outputs/logs", exist_ok=True)
    logging.basicConfig(
        filename="outputs/logs/run.log",
        filemode="w",
        level=logging.INFO,
        format='%(asctime)s - %(message)s'
    )
    return logging.getLogger("AgentLogger")

logger = setup_logger()