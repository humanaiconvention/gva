"""Spawned actor process with an explicit, narrow IPC boundary in both V arms.

This is separation for a fixed trusted optimizer, not an OS sandbox for adversarial
code. Python/OS and same-user filesystem protection are trusted infrastructure.
"""
import multiprocessing as mp
from .optimizers.finite_search import actor_worker


class ActorProcess:
    def __enter__(self):
        context = mp.get_context("spawn")
        self.connection, child = context.Pipe()
        self.process = context.Process(target=actor_worker, args=(child,), daemon=True)
        self.process.start()
        child.close()
        if self.recv() != "ready":
            raise RuntimeError("Actor initialization failed")
        return self

    def recv(self):
        if not self.connection.poll(60):
            raise RuntimeError("Actor IPC timeout: infrastructure failure")
        return self.connection.recv()

    def choose(self, observation, candidates, service):
        self.connection.send((observation, candidates))
        message, requests = self.recv()
        if message != "preview" or requests != candidates:
            raise RuntimeError("Actor protocol violation")
        batch = service.batch(requests, service.token)
        self.connection.send(batch)
        message, action_id, score, cpu_seconds = self.recv()
        self.last_cpu_seconds = cpu_seconds
        if message != "chosen" or action_id not in candidates:
            raise RuntimeError("Actor protocol violation")
        return action_id, score

    def __exit__(self, *args):
        if self.process.is_alive():
            try:
                self.connection.send(None)
            except (BrokenPipeError, EOFError):
                pass
        self.process.join(3)
        if self.process.is_alive():
            self.process.terminate()
            self.process.join()
        self.connection.close()
