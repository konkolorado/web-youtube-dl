from __future__ import annotations

import logging
from pathlib import Path

import janus

logger = logging.getLogger(__name__)
_queues: dict[str, janus.Queue] = {}


class ProgressQueues:
    QUEUE_SENTINAL = 100

    def track(self, filename: str):
        global _queues
        filepath = Path(filename)
        if filepath.stem not in _queues:
            _queues[filepath.stem] = janus.Queue()
            logger.debug(f"Tracking {filename} download as {filepath.stem}")

    def put(self, filename: str, value: float):
        filepath = Path(filename)
        _queues[filepath.stem].sync_q.put(value)
        logger.debug(f"Updated {filename} download as {filepath.stem}")

    def terminate(self, filename: str):
        filepath = Path(filename)
        _queues[filepath.stem].sync_q.put(self.QUEUE_SENTINAL)
        # _queues.pop(filepath.stem) # noqa
        logger.debug(f"Terminated {filename} download as {filepath.stem}")

    async def get(self, filename) -> float:
        filepath = Path(filename)
        q = _queues[filepath.stem]

        result = await q.async_q.get()
        q.async_q.task_done()
        return result
