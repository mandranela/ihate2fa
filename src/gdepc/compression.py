
import json
from typing import List
from gdepc.settings import datasets, DATASETS_PATH, compression_dict, GENERATED_PATH
import pandas as pd
import logging
from gdepc.pack import Packaging, compress_bytes, CompressionData, PackageMessageData
import multiprocessing as mp
from multiprocessing.pool import Pool, AsyncResult

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(f"{__name__}")
logger.setLevel(logging.INFO)

packaging = Packaging()
# logger.info(f"[{input_data.compression_name}]: " + f"{data.json_message_size = }")
# logger.info(f"[{input_data.compression_name}]: " + f"{data.compressed_json_message_size = }")
# logger.info(f"[{input_data.compression_name}]: " + f"{data.json_compression_time = }")
# logger.info(f"[{input_data.compression_name}]: " + f"{data.proto_message_size = }")
# logger.info(f"[{input_data.compression_name}]: " + f"{data.compressed_proto_message_size = }")
# logger.info(f"[{input_data.compression_name}]: " + f"{data.proto_compression_time = }")
# logger.info(f"[{input_data.compression_name}]: " + f"{data.descriptor_size = }")
# logger.info(f"[{input_data.compression_name}]: " + f"{data.compressed_descriptor_message_size = }")
# logger.info(f"[{input_data.compression_name}]: " + f"{data.descriptor_compression_time = }")



def start_compression(pool: Pool):
    analytic_data = []
    tasks: List[AsyncResult] = []
    for dataset_name in datasets:
        
        dataset_file_name = datasets[dataset_name]
        logger.info(f"Start compression {dataset_name}")
        dataset_file_path = DATASETS_PATH + '/' + dataset_file_name
        df = pd.read_csv(dataset_file_path)
        for key, row in df[:10000].iterrows():
            json_message = row.to_dict()
            message = packaging.pack_message(json_message)
            cmp_data = CompressionData()
            cmp_data.json_bytes = json.dumps(json_message).encode()
            cmp_data.proto_bytes = message.proto_message.SerializeToString()
            cmp_data.descriptor_bytes = message.descriptor.SerializeToString()
            starmap_data = [(cmp_data, compression_name, dataset_name, key) for compression_name in list(compression_dict.keys())]
            analytic_datas_tasks = pool.starmap_async(compress_bytes, starmap_data)
            tasks.append(analytic_datas_tasks)

    for task in tasks:
        results: List[PackageMessageData] = task.get()
        for result in results:
            analytic_data.append(result.to_dict_analytic())
        logger.info(f"Data loaded {len(analytic_data)}")
    return analytic_data
            # for compression_name, compression_func in text_compression.items():
            #     data = message.compress_huffman(compression_func)
            #     logger.info(f"[{compression_name}]: " + f"{data.json_message_size = }")
            #     for compression_name_inner, compression_func_inner in compression_dict.items():
            #         logger.info(f"[{compression_name}] [{compression_name_inner}]: " + f"compressed inner {len(compression_func_inner(data.compressed_json_message))}")
            #     logger.info(f"[{compression_name}]: " + f"{data.compressed_json_message_size = }")
            #     logger.info(f"[{compression_name}]: " + f"{data.json_compression_time = }")

            #     logger.info(f"[{compression_name}]: " + f"{data.proto_message_size = }")
            #     for compression_name_inner, compression_func_inner in compression_dict.items():
            #         logger.info(f"[{compression_name}] [{compression_name_inner}]: " + f"compressed inner {len(compression_func_inner(data.compressed_proto_message))}")
            #     logger.info(f"[{compression_name}]: " + f"{data.compressed_proto_message_size = }")
            #     logger.info(f"[{compression_name}]: " + f"{data.proto_compression_time = }")

            #     logger.info(f"[{compression_name}]: " + f"{data.descriptor_size = }")
            #     for compression_name_inner, compression_func_inner in compression_dict.items():
            #         logger.info(f"[{compression_name}] [{compression_name_inner}]: " + f"compressed inner {len(compression_func_inner(data.compressed_descriptor))}")
            #     logger.info(f"[{compression_name}]: " + f"{data.compressed_descriptor_message_size = }")
            #     logger.info(f"[{compression_name}]: " + f"{data.descriptor_compression_time = }")
            #     data.compression = compression_name
            #     data.dataset_name = dataset_name
            #     data.dataset_message_index = key
            #     analytic_data.append(data.to_dict_analytic())

if __name__ == '__main__':
    analytic_data = []

    with mp.Pool(mp.cpu_count() * 2) as pool:
        data = start_compression(pool)

    
    analytic_df = pd.DataFrame(data)
    analytic_df.to_csv(GENERATED_PATH + '/compression_analytic_data.csv', index=False)
        