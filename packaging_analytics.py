import pandas as pd


if __name__ == "__main__":

    df_brotli = pd.read_csv(
        "/Users/vladislavkovazin/miem/gdepc/static/analytics/packaging_brotli_1960.csv"
    )
    df_gzip = pd.read_csv(
        "/Users/vladislavkovazin/miem/gdepc/static/analytics/packaging_gzip_1960.csv"
    )
    df_lzma = pd.read_csv(
        "/Users/vladislavkovazin/miem/gdepc/static/analytics/packaging_lzma_1960.csv"
    )

    df_brotli_no_descriptors_1960 = pd.read_csv(
        "/Users/vladislavkovazin/miem/gdepc/static/analytics/packaging_brotli_no_descriptors_1960.csv"
    )
    df_brotli_no_descriptors_360 = pd.read_csv(
        "/Users/vladislavkovazin/miem/gdepc/static/analytics/packaging_brotli_no_descriptors_360.csv"
    )

    df_gzip_no_descriptors_1960 = pd.read_csv(
        "/Users/vladislavkovazin/miem/gdepc/static/analytics/packaging_gzip_no_descriptors_1960.csv"
    )
    df_gzip_no_descriptors_360 = pd.read_csv(
        "/Users/vladislavkovazin/miem/gdepc/static/analytics/packaging_gzip_no_descriptors_360.csv"
    )

    df_lzma_no_descriptors_1960 = pd.read_csv(
        "/Users/vladislavkovazin/miem/gdepc/static/analytics/packaging_lzma_no_descriptors_1960.csv"
    )
    df_lzma_no_descriptors_360 = pd.read_csv(
        "/Users/vladislavkovazin/miem/gdepc/static/analytics/packaging_lzma_no_descriptors_360.csv"
    )

    print(f"{df_brotli['package_messages'].agg('mean') = }")
    print(f"{df_brotli_no_descriptors_1960['package_messages'].agg('mean') = }")
    print(f"{df_brotli_no_descriptors_360['package_messages'].agg('mean') = }")

    print(f"{df_gzip['package_messages'].agg('mean') = }")
    print(f"{df_gzip_no_descriptors_1960['package_messages'].agg('mean') = }")
    print(f"{df_gzip_no_descriptors_360['package_messages'].agg('mean') = }")

    print(f"{df_lzma['package_messages'].agg('mean') = }")
    print(f"{df_lzma_no_descriptors_1960['package_messages'].agg('mean') = }")
    print(f"{df_lzma_no_descriptors_360['package_messages'].agg('mean') = }")
