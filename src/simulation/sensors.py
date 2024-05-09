from asyncio import Queue
import asyncio
import json
import os
from typing import List
from settings import datasets
from packaging.main import Packaging
from random import shuffle


class SensorsBrokerSimulation:
    queue: Queue[dict]
    packaging: Packaging

    def __init__(self, queue: Queue) -> None:
        self.queue = queue

    def load_datasets(self):
        packaging = Packaging()
        for dataset_name in datasets:
            packaging.add_df(dataset_name)
        self.packaging = packaging

    def create_test_messages(self, number):
        if os.path.isfile(
            "/Users/vladislavkovazin/miem/gdepc/static/datasets/packaging_test_dataset.json"
        ):
            return

        adding_messages = []
        for dataset_name in datasets:
            data = self.packaging.get_messages_data(dataset_name, number)
            adding_messages.extend(
                [message.to_dict() for _, message in data.iterrows()]
            )

        shuffle(adding_messages)

        with open(
            "/Users/vladislavkovazin/miem/gdepc/static/datasets/packaging_test_dataset.json",
            "w",
        ) as file:
            json.dump(adding_messages, file)

    def get_test_messages(self) -> list:
        if os.path.isfile(
            "/Users/vladislavkovazin/miem/gdepc/static/datasets/packaging_test_dataset.json"
        ):
            with open(
                "/Users/vladislavkovazin/miem/gdepc/static/datasets/packaging_test_dataset.json",
                "r",
            ) as file:
                return json.load(file)

        return None

    async def add_to_queue(self, messages: List[dict]):
        for message in messages:
            await self.queue.put(message)

    async def main(self):
        messages = self.get_test_messages()
        while len(messages) > 0:
            for _ in range(10):
                await self.queue.put(messages.pop())
            await asyncio.sleep(0.5)
