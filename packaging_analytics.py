import math
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == "__main__":

    compression_decompression = [
        "no_compression",
        "lzma",
        "gzip",
        "zlib",
        "brotli",
    ]

    number_of_packed_containers_with_descriptions = []
    number_of_packed_containers_no_descriptions = []
    number_of_packed_containers_json = []

    not_occupied_space_descr = []
    not_occupied_space_no_descr = []
    not_occupied_space_json = []

    packed_messages_descr = []
    packed_messages_no_descr = []
    packed_messages_json = []

    index = []

    for key in compression_decompression:
        index.append(key)

        df_packaging_simulation = pd.read_csv(
            f"/Users/vladislavkovazin/miem/gdepc/static/analytics/packaging_simulation_bnb_{key}.csv"
        )
        df_with_desc = (
            df_packaging_simulation[df_packaging_simulation["with_descriptors"] == True]
            .drop("with_descriptors", axis=1)
            .reset_index()
        )
        df_without_desc = (
            df_packaging_simulation[
                df_packaging_simulation["with_descriptors"] == False
            ]
            .drop("with_descriptors", axis=1)
            .reset_index()
        )

        print(f"{key} with descr")
        df = df_with_desc[df_packaging_simulation["compression"] == key]
        number_of_packed_containers_with_descriptions.append(len(df))
        not_occupied_space_descr.append(abs(1960 - df["package_size"].agg("mean")))
        packed_messages_descr.append(df["packed_messages"].agg("mean"))

        print(f"{df['packed_messages'].agg('sum') = }")
        print(f"{df['packed_messages'].agg('mean') = }")
        print(f"{df['package_size'].agg('mean') = }")
        print(f"{len(df) = }")
        print()

        print(f"{key} without descr")
        df = df_without_desc[df_packaging_simulation["compression"] == key]
        number_of_packed_containers_no_descriptions.append(len(df))
        not_occupied_space_no_descr.append(abs(1960 - df["package_size"].agg("mean")))
        packed_messages_no_descr.append(df["packed_messages"].agg("mean"))

        print(f"{df['packed_messages'].agg('sum') = }")
        print(f"{df['packed_messages'].agg('mean') = }")
        print(f"{df['package_size'].agg('mean') = }")
        print(f"{len(df) = }")
        print()

        df_packaging_simulation = pd.read_csv(
            f"/Users/vladislavkovazin/miem/gdepc/static/analytics/packaging_simulation_bnb_{key}_json.csv"
        )
        df_without_desc = (
            df_packaging_simulation[
                df_packaging_simulation["with_descriptors"] == False
            ]
            .drop("with_descriptors", axis=1)
            .reset_index()
        )

        print(f"{key} json")
        df = df_without_desc[df_packaging_simulation["compression"] == key + "_json"]
        number_of_packed_containers_json.append(len(df))
        not_occupied_space_json.append(abs(1960 - df["package_size"].agg("mean")))
        packed_messages_json.append(df["packed_messages"].agg("mean"))

        print(f"{df['packed_messages'].agg('sum') = }")
        print(f"{df['packed_messages'].agg('mean') = }")
        print(f"{df['package_size'].agg('mean') = }")
        print(f"{len(df) = }")
        print()

    axes = pd.DataFrame(
        {
            "with_descriptions": number_of_packed_containers_with_descriptions,
            "no_descriptions": number_of_packed_containers_no_descriptions,
            "json": number_of_packed_containers_json,
        },
        index=index,
    ).plot.bar(
        rot=0,
        title="Количество контейнеров, в которые упаковали 7500 сообщений из разных датасетов",
    )

    pd.DataFrame(
        {
            "with_descriptions": not_occupied_space_descr,
            "no_descriptions": not_occupied_space_no_descr,
            "json": not_occupied_space_json,
        },
        index=index,
    ).plot.bar(rot=0, title="Количество незанятого места в контейнере")

    axes = pd.DataFrame(
        {
            "with_descriptions": packed_messages_descr,
            "no_descriptions": packed_messages_no_descr,
            "json": packed_messages_json,
        },
        index=index,
    ).plot.bar(rot=0, title="Количество упакованных сообщений в одном контейнере")
    plt.show()
