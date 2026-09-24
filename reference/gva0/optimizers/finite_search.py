"""Actor code: no simulator, evaluator, regime, seed, filesystem, or latent inputs."""
from . import model_api
from ..objective import average_scores
from ..actions import NOOP
from time import process_time


def select(batch):
    averages = tuple(average_scores(s) for s in batch.scores)
    winner = max(range(len(batch.action_ids)), key=lambda j: (averages[j], batch.action_ids[j] == NOOP, -batch.action_ids[j]))
    return batch.action_ids[winner], averages[winner]


def choose(observation, candidates, preview):
    return select(preview.batch(candidates))[0]


def actor_worker(connection):
    connection.send("ready")
    while True:
        command = connection.recv()
        if command is None:
            return
        observation, candidates = command
        connection.send(("preview", candidates))
        batch = connection.recv()
        started = process_time()
        result = select(batch)
        connection.send(("chosen", *result, process_time() - started))
