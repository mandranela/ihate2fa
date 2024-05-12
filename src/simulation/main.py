from asyncio import Queue
import asyncio
import lzma
from multiprocessing import Pool, cpu_count
import zlib

import pandas as pd
from simulation.sensors import SensorsBrokerSimulation
from simulation.gateway import GDEPCSimulation
from simulation.client import Client
import logging

from settings import compression_decompression


async def data_collecting(
    gateway: GDEPCSimulation, compression: str, with_descriptors, logger
):

    analytic_datas = []
    message_counts = 0
    try:
        while True:
            if gateway.input_queue.empty():
                await asyncio.sleep(2)
                flushed = await gateway.flush()

                while not gateway.result_queue.empty():
                    message = await gateway.result_queue.get()
                    analytic_data = {}
                    analytic_data["packed_messages"] = len(message.message_sizes)
                    analytic_data["package_size"] = message.ByteSize()
                    analytic_data["container_size"] = gateway.knapsack.max_container
                    analytic_data["compression"] = compression
                    analytic_data["with_descriptors"] = with_descriptors

                    analytic_datas.append(analytic_data)

                for message in flushed:
                    analytic_data = {}
                    analytic_data["packed_messages"] = len(message.message_sizes)
                    analytic_data["package_size"] = message.ByteSize()
                    analytic_data["container_size"] = gateway.knapsack.max_container
                    analytic_data["compression"] = compression
                    analytic_data["with_descriptors"] = with_descriptors

                    analytic_datas.append(analytic_data)

                break

            while not gateway.result_queue.empty():
                message = await gateway.result_queue.get()
                analytic_data = {}
                analytic_data["packed_messages"] = len(message.message_sizes)
                message_counts += len(message.message_sizes)
                analytic_data["package_size"] = message.ByteSize()
                analytic_data["container_size"] = gateway.knapsack.max_container
                analytic_data["compression"] = compression
                analytic_data["with_descriptors"] = with_descriptors
                analytic_datas.append(analytic_data)
                gateway.result_queue.task_done()
                logger.info(f"Осталось сообщений {gateway.input_queue.qsize()}")
                logger.info(f"Сообщений упаковано {message_counts}")

            await asyncio.sleep(2)

    finally:
        return analytic_datas


async def start_simulation(compression, with_descriptors, json_structure):

    logging.basicConfig()
    logger = logging.getLogger(f"[{with_descriptors = }] [{compression}] simulation")
    logger.setLevel(logging.INFO)
    client = Client(compression)
    input_queue = Queue()
    sensors = SensorsBrokerSimulation(input_queue)
    data = sensors.get_test_messages()

    if not data:
        sensors.load_datasets()
        sensors.create_test_messages(500)
    await sensors.add_to_queue(data)

    gdepc = GDEPCSimulation(
        input_queue, logger, compression, with_descriptors, json_structure
    )
    # sensors_task = asyncio.create_task(sensors.main())
    gateway_task = asyncio.create_task(gdepc.packing())
    # client_task = asyncio.create_task(client.main())
    data = await data_collecting(gdepc, compression, with_descriptors, logger)
    return data
    # try:
    #     while True:
    #         if gateway_task.done():
    #             return
    #         message = await gdepc.result_queue.get()
    #         await client.iridium_comm.put(message.SerializeToString())
    # finally:
    #     sensors_task.cancel()
    #     gateway_task.cancel()

    #     while not gdepc.result_queue.empty():
    #         message = await gdepc.result_queue.get()
    #         await client.iridium_comm.put(message.SerializeToString())

    #     while not gdepc.not_fully_packed.empty():
    #         message = await gdepc.not_fully_packed.get()
    #         await client.iridium_comm.put(message.SerializeToString())

    #     client_task.cancel()


def main(compression, with_descriptors, json_structure):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(
        start_simulation(compression, with_descriptors, json_structure)
    )


if __name__ == "__main__":

    with Pool(cpu_count()) as pool:
        args_map = [
            (compression, False, True)
            for compression in list(compression_decompression.keys())
        ]

        result = pool.starmap(main, args_map)
    data = []
    [data.extend(item) for item in result]
    analytic_data = pd.DataFrame(data)
    analytic_data.to_csv(
        f"/Users/vladislavkovazin/miem/gdepc/static/analytics/packaging_simulation.csv"
    )
