from app.environmental_data import EnvironmentalDataAnalyzer


def main() -> None:
    analyzer = EnvironmentalDataAnalyzer()

    print(f"\nWorld map loaded: {analyzer.world_map.shape}")
    print(f"Datasets loaded: {list(analyzer.datasets.keys())}")
    print(f"Merged datasets: {list(analyzer.merged_data.keys())}")


if __name__ == "__main__":
    main()