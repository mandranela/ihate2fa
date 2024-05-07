
import pandas as pd
import matplotlib.pyplot as plt


if __name__ == "__main__":
    # subprocess.run(["mkdir", "-p", f"{GENERATED_PATH}/generated"])

    # combine_self_described_message()
    # subprocess.run(["rm", "-rf", f"{GENERATED_PATH}/generated"])

    
    df_brotli = pd.read_csv('/Users/vladislavkovazin/miem/gdepc/static/analytics/packaging_brotli.csv')
    df_gzip = pd.read_csv('/Users/vladislavkovazin/miem/gdepc/static/analytics/packaging_gzip.csv')
    df_lzma = pd.read_csv('/Users/vladislavkovazin/miem/gdepc/static/analytics/packaging_lzma.csv')

    df_brotli_no_descriptors = pd.read_csv('/Users/vladislavkovazin/miem/gdepc/static/analytics/packaging_brotli_no_descriptors.csv')
    df_gzip_no_descriptors = pd.read_csv('/Users/vladislavkovazin/miem/gdepc/static/analytics/packaging_gzip_no_descriptors.csv')
    df_lzma_no_descriptors = pd.read_csv('/Users/vladislavkovazin/miem/gdepc/static/analytics/packaging_lzma_no_descriptors.csv')


    print(f"{df_brotli['package_messages'].agg('mean') = }")
    print(f"{df_brotli_no_descriptors['package_messages'].agg('mean') = }")
    print(f"{df_gzip['package_messages'].agg('mean') = }")
    print(f"{df_gzip_no_descriptors['package_messages'].agg('mean') = }")
    print(f"{df_lzma['package_messages'].agg('mean') = }")
    print(f"{df_lzma_no_descriptors['package_messages'].agg('mean') = }")
