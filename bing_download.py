from bing_image_downloader import downloader


downloader.download(
    "mealybug insect pest",
    limit=100,
    output_dir="dataset_new",
    adult_filter_off=True,
    force_replace=False,
    timeout=10
)