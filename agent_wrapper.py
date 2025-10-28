"""
Agent Wrapper Module
Provides retry and timeout logic for agent calls.
"""

import time
from typing import Tuple, Callable, Any
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
import config


class AgentTimeoutError(Exception):
    """Raised when an agent call times out."""
    pass


class AgentMaxRetriesError(Exception):
    """Raised when an agent exceeds maximum retry attempts."""
    pass


class AgentWrapper:
    """Wrapper for agent calls with retry and timeout logic."""

    def __init__(self,
                 max_retries: int = None,
                 timeout: int = None,
                 retry_delay: int = None):
        """
        Initialize the agent wrapper.

        Args:
            max_retries: Maximum number of retry attempts
            timeout: Timeout in seconds for each agent call
            retry_delay: Delay in seconds between retries
        """
        self.max_retries = max_retries or config.MAX_RETRIES
        self.timeout = timeout or config.AGENT_TIMEOUT
        self.retry_delay = retry_delay or config.RETRY_DELAY

    def call_with_retry(self,
                       agent_func: Callable,
                       *args,
                       **kwargs) -> Tuple[bool, Any]:
        """
        Call an agent function with retry logic and timeout.

        Args:
            agent_func: The agent function to call
            *args: Positional arguments for the agent function
            **kwargs: Keyword arguments for the agent function

        Returns:
            Tuple of (success: bool, result: Any)
            - On success: (True, translated_text)
            - On failure: (False, error_message)

        Raises:
            AgentTimeoutError: If all retries timeout
            AgentMaxRetriesError: If max retries exceeded
        """
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                # Call agent with timeout
                result = self._call_with_timeout(agent_func, *args, **kwargs)
                return (True, result)

            except FuturesTimeoutError:
                last_error = f"Timeout ({self.timeout}s) on attempt {attempt}/{self.max_retries}"
                print(f"  ⚠ {last_error}")

                if attempt == self.max_retries:
                    error_msg = f"Agent timeout after {self.max_retries} attempts ({self.timeout}s each)"
                    raise AgentTimeoutError(error_msg)

                # Wait before retrying
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)

            except Exception as e:
                last_error = f"Error on attempt {attempt}/{self.max_retries}: {str(e)}"
                print(f"  ⚠ {last_error}")

                if attempt == self.max_retries:
                    error_msg = f"Agent failed after {self.max_retries} attempts. Last error: {str(e)}"
                    raise AgentMaxRetriesError(error_msg)

                # Wait before retrying
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)

        # Should not reach here, but just in case
        return (False, last_error)

    def _call_with_timeout(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call a function with timeout using ThreadPoolExecutor.

        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            TimeoutError: If function call exceeds timeout
        """
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args, **kwargs)
            try:
                result = future.result(timeout=self.timeout)
                return result
            except FuturesTimeoutError:
                future.cancel()
                raise


class AgentCallResult:
    """Container for agent call results with metadata."""

    def __init__(self,
                 success: bool,
                 translation: str = None,
                 attempts: int = 0,
                 duration: float = 0.0,
                 error: str = None):
        """
        Initialize agent call result.

        Args:
            success: Whether the call succeeded
            translation: The translated text (if successful)
            attempts: Number of attempts made
            duration: Total duration in seconds
            error: Error message (if failed)
        """
        self.success = success
        self.translation = translation
        self.attempts = attempts
        self.duration = duration
        self.error = error

    def __repr__(self):
        if self.success:
            return f"AgentCallResult(success=True, attempts={self.attempts}, duration={self.duration:.2f}s)"
        else:
            return f"AgentCallResult(success=False, error='{self.error}')"
