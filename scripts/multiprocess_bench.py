import subprocess
import sys


def run_scraping_processes(site_names: list[str]):
    processes = []

    for site_name in site_names:
        print("Starting a new scraping process...")
        process = subprocess.Popen(
            [sys.executable, "-m", "bin.scrape_recipes", site_name]
        )
        processes.append(process)

    for process in processes:
        process.wait()


if __name__ == "__main__":
    sites_names = ["NYTimes Cooking", "BBCFood", "BBCGoodFood", "Food", "BonAppetit"]

    print(f"Running {len(sites_names)} concurrent scraping processes...")
    run_scraping_processes(sites_names)
    print("All scraping processes have completed.")
