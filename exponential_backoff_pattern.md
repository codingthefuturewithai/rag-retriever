# Implementing Exponential Backoff with LangChain and OpenAI

This guide shows how to implement exponential backoff for OpenAI API calls using the `tenacity` library with LangChain.

## Configuration

First, add these settings to your configuration:

```yaml
# OpenAI API retry settings
openai_api:
  max_retries: 3
  retry_delay: 5.0 # Base delay in seconds
  max_delay: 60 # Maximum delay in seconds
```

## Implementation

1. Install the required package:

```bash
pip install tenacity
```

2. Import necessary modules:

```python
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)
```

3. Create a decorator for your LangChain wrapper class:

```python
@retry(
    stop=stop_after_attempt(lambda: config["openai_api"]["max_retries"]),
    wait=wait_exponential(
        multiplier=lambda: config["openai_api"]["retry_delay"],
        min=1,
        max=config["openai_api"]["max_delay"]
    ),
    # Only retry on rate limit or quota errors
    retry=lambda e: "rate limit" in str(e).lower() or "quota" in str(e).lower(),
    before_sleep=lambda retry_state: logger.info(
        "Rate limit error encountered. Using exponential backoff strategy:"
        "\n  - Attempt: %d/%d"
        "\n  - Next retry in: %.1f seconds"
        "\n  - Base delay: %.1f seconds"
        "\n  - Max delay: %d seconds",
        retry_state.attempt_number + 1,
        config["openai_api"]["max_retries"],
        retry_state.next_action.sleep,
        config["openai_api"]["retry_delay"],
        config["openai_api"]["max_delay"]
    ),
)
def your_langchain_method(self, ...):
    # Your existing method implementation
    pass
```

## How It Works

1. The `@retry` decorator will catch any exceptions that match the `retry` condition
2. If a rate limit or quota error occurs:
   - It will wait using exponential backoff (base_delay \* 2^attempt)
   - The delay starts at your configured retry_delay (e.g., 5 seconds)
   - Each retry doubles the previous delay
   - The delay is capped at max_delay (e.g., 60 seconds)
   - After max_retries attempts, it will raise the last error
3. The `before_sleep` function logs detailed information about each retry attempt

## Example Usage

```python
class YourLangChainWrapper:
    @retry(...)  # Add the decorator as shown above
    def generate_response(self, prompt: str) -> str:
        try:
            response = self.llm.generate(prompt)
            return response
        except Exception as e:
            logger.error(f"Error in OpenAI API call: {str(e)}")
            raise
```

## Benefits

- Gracefully handles OpenAI API rate limits
- Exponential backoff reduces API pressure during high load
- Configurable retry parameters
- Detailed logging of retry attempts
- Clean separation of retry logic from business logic
