"""Same request/batch action boundary, with multiple bounded preview requests."""
import multiprocessing as mp
from .actions import CATALOGUE
from .optimizers.stochastic_beam import worker


class BeamActor:
    def __enter__(self):
        parent, child = mp.get_context("spawn").Pipe()
        self.connection = parent
        self.process = mp.get_context("spawn").Process(target=worker, args=(child,), daemon=True)
        self.process.start()
        child.close()
        if self.recv() != "ready":
            raise RuntimeError("Beam actor initialization failed")
        return self

    def recv(self):
        if not self.connection.poll(60):
            raise RuntimeError("Beam actor timeout")
        return self.connection.recv()

    def choose(self, service, private_seed, budget=48):
        ids = tuple(range(48))
        self.connection.send((ids, tuple(a.key for a in CATALOGUE), budget, private_seed))
        evaluated = set()
        while True:
            message = self.recv()
            if message[0] == "preview":
                requests = message[1]
                if any(type(a) is not int or a not in ids or a in evaluated for a in requests) or len(set(requests)) != len(requests) or len(evaluated) + len(requests) > budget:
                    raise RuntimeError("Beam violated query budget or catalogue")
                evaluated.update(requests)
                self.connection.send(service.batch(requests, service.token))
            elif message[0] == "chosen":
                _, action, score, checkpoints, cpu = message
                if len(evaluated) != budget or action not in evaluated:
                    raise RuntimeError("Incomplete beam budget")
                self.last_cpu_seconds = cpu
                return action, score, checkpoints
            else:
                raise RuntimeError("Invalid beam protocol")

    def __exit__(self, *args):
        if self.process.is_alive():
            self.connection.send(None)
        self.process.join(3)
        if self.process.is_alive():
            self.process.terminate()
            self.process.join()
        self.connection.close()
