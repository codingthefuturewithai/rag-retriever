from rag_retriever.document_processor.vision_analyzer import VisionAnalyzer
from rag_retriever.utils.config import config
import json


def analyze_test_image(image_path: str):
    """Test the vision analyzer with a sample image."""

    # Initialize the analyzer with the same config used by CLI
    analyzer = VisionAnalyzer(config._config)

    # Analyze the image
    result = analyzer.analyze_image(image_path)

    if result:
        # Pretty print the analysis results
        print("\nImage Analysis Results:")
        print("----------------------")
        print(json.dumps(result, indent=2))
    else:
        print(f"Failed to analyze image: {image_path}")


if __name__ == "__main__":
    # Replace with your image path
    test_image = "./tests/data/images/post-scaffolding-sprint-workflow.png"

    print(f"Analyzing image: {test_image}")
    analyze_test_image(test_image)
