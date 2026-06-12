"""
Inter-process communication for JARVIS multiprocessing workers.
Main process owns GUI and TTS; workers send messages via queues.
"""
from enum import Enum
from typing import Optional

from multiprocessing import Queue, Event


class MsgType(Enum):
    SPEAK = "speak"
    STATUS = "status"
    ANIMATION = "animation"
    SHUTDOWN = "shutdown"


_speak_queue: Optional[Queue] = None
_status_queue: Optional[Queue] = None
_speak_done: Optional[Event] = None


def init_ipc(speak_queue: Queue, status_queue: Queue, speak_done_event: Event) -> None:
    """Wire IPC queues. Called in main before spawning workers and at each worker entry."""
    global _speak_queue, _status_queue, _speak_done
    _speak_queue = speak_queue
    _status_queue = status_queue
    _speak_done = speak_done_event


def queue_speak(text: str, timeout: float = 120) -> None:
    """Worker: request TTS playback on main process and block until done."""
    if _speak_queue is None or _speak_done is None:
        raise RuntimeError("IPC not initialized — call init_ipc() first")
    _speak_done.clear()
    _speak_queue.put((MsgType.SPEAK, text))
    _speak_done.wait(timeout=timeout)


def queue_status(text: str) -> None:
    """Worker: update the HUD status label on main process."""
    if _status_queue is None:
        raise RuntimeError("IPC not initialized — call init_ipc() first")
    _status_queue.put((MsgType.STATUS, text))


def queue_animation(state: str) -> None:
    """Worker: update arc-reactor animation state on main process."""
    if _status_queue is None:
        raise RuntimeError("IPC not initialized — call init_ipc() first")
    _status_queue.put((MsgType.ANIMATION, state))


def queue_shutdown() -> None:
    """Worker: request graceful shutdown of the main GUI process."""
    if _status_queue is None:
        raise RuntimeError("IPC not initialized — call init_ipc() first")
    _status_queue.put((MsgType.SHUTDOWN, None))
