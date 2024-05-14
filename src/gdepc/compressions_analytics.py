import math
import pandas as pd
import matplotlib.pyplot as plt
from gdepc.settings import datasets

if __name__ == "__main__":
    df = pd.read_csv("/home/vvkovyazin/gdepc/compression_analytic_data.csv")
    compression = 'zopfli'
    for dataset in datasets:
        print(dataset)
        print('proto_message_size')
        print('max', df[(df['compression'] == compression) & (df['dataset_name'] == dataset)]['proto_message_size'].agg(['max'])['max'])
        print('mean', df[(df['compression'] == compression) & (df['dataset_name'] == dataset)]['proto_message_size'].agg(['mean'])['mean'])
        print('compressed_proto_message_size')
        print('max', df[(df['compression'] == compression) & (df['dataset_name'] == dataset)]['compressed_proto_message_size'].agg(['max'])['max'])
        print('mean', df[(df['compression'] == compression) & (df['dataset_name'] == dataset)]['compressed_proto_message_size'].agg(['mean'])['mean'])

    # axes = pd.DataFrame(
    #     {
    #         "with_descriptions": number_of_packed_containers_with_descriptions,
    #         "no_descriptions": number_of_packed_containers_no_descriptions,
    #         "json": number_of_packed_containers_json,
    #     },
    #     index=index,
    # ).plot.bar(
    #     rot=0,
    #     title="Количество контейнеров, в которые упаковали 7500 сообщений из разных датасетов",
    # )

    # pd.DataFrame(
    #     {
    #         "with_descriptions": not_occupied_space_descr,
    #         "no_descriptions": not_occupied_space_no_descr,
    #         "json": not_occupied_space_json,
    #     },
    #     index=index,
    # ).plot.bar(rot=0, title="Количество незанятого места в контейнере")

    # axes = pd.DataFrame(
    #     {
    #         "with_descriptions": packed_messages_descr,
    #         "no_descriptions": packed_messages_no_descr,
    #         "json": packed_messages_json,
    #     },
    #     index=index,
    # ).plot.bar(rot=0, title="Количество упакованных сообщений в одном контейнере")
    # plt.show()
