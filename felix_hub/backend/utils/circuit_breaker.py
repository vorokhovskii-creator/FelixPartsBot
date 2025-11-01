"""
Circuit breaker pattern implementation for external API calls.
"""
import time
import logging
from enum import Enum
from typing import Callable, Any, Optional
from threading import Lock

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Too many failures, reject calls
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures.
    
    When too many failures occur, the circuit "opens" and stops making calls
    to the failing service for a timeout period. After the timeout, it enters
    "half-open" state to test if the service recovered.
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        half_open_attempts: int = 3
    ):
        """
        Initialize circuit breaker.
        
        Args:
            name: Name of the circuit breaker (for logging)
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before trying again (in open state)
            half_open_attempts: Number of successful attempts needed to close circuit
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_attempts = half_open_attempts
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.lock = Lock()
    
    def call(self, func: Callable, *args, **kwargs):
        """
        Execute function through circuit breaker.
        
        Returns:
            Tuple of (success: bool, result: Any)
            If circuit is open, returns (False, None)
        """
        with self.lock:
            # Check if we should attempt the call
            if self.state == CircuitState.OPEN:
                # Check if timeout has elapsed
                if time.time() - self.last_failure_time >= self.timeout:
                    logger.info(f"Circuit breaker {self.name}: Transitioning to HALF_OPEN")
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    logger.warning(
                        f"Circuit breaker {self.name}: Circuit OPEN, rejecting call "
                        f"(failures: {self.failure_count})"
                    )
                    return False, None
        
        # Attempt the call
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return True, result
        except Exception as e:
            self._on_failure()
            logger.error(f"Circuit breaker {self.name}: Call failed: {e}")
            raise
    
    def _on_success(self):
        """Handle successful call."""
        with self.lock:
            self.failure_count = 0
            
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                logger.debug(
                    f"Circuit breaker {self.name}: Success in HALF_OPEN "
                    f"({self.success_count}/{self.half_open_attempts})"
                )
                
                if self.success_count >= self.half_open_attempts:
                    logger.info(f"Circuit breaker {self.name}: Transitioning to CLOSED")
                    self.state = CircuitState.CLOSED
                    self.success_count = 0
    
    def _on_failure(self):
        """Handle failed call."""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                logger.warning(
                    f"Circuit breaker {self.name}: Failure in HALF_OPEN, "
                    f"transitioning back to OPEN"
                )
                self.state = CircuitState.OPEN
                self.success_count = 0
            
            elif self.state == CircuitState.CLOSED:
                if self.failure_count >= self.failure_threshold:
                    logger.error(
                        f"Circuit breaker {self.name}: Failure threshold reached "
                        f"({self.failure_count}), transitioning to OPEN"
                    )
                    self.state = CircuitState.OPEN
    
    def get_state(self) -> CircuitState:
        """Get current circuit breaker state."""
        return self.state
    
    def reset(self):
        """Manually reset circuit breaker to closed state."""
        with self.lock:
            logger.info(f"Circuit breaker {self.name}: Manual reset to CLOSED")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
    
    def get_metrics(self) -> dict:
        """Get circuit breaker metrics."""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': self.last_failure_time
        }


# Global circuit breakers for different services
_circuit_breakers = {}
_breakers_lock = Lock()


def get_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    timeout: float = 60.0
):
    """
    Get or create a circuit breaker by name.
    
    Args:
        name: Circuit breaker name
        failure_threshold: Number of failures before opening
        timeout: Seconds to wait before retrying
    
    Returns:
        CircuitBreaker instance
    """
    with _breakers_lock:
        if name not in _circuit_breakers:
            _circuit_breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                timeout=timeout
            )
        return _circuit_breakers[name]


def get_all_circuit_breakers():
    """Get all registered circuit breakers."""
    return _circuit_breakers.copy()
