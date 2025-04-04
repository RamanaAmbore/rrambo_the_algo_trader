import threading
from src.helpers.logger import get_logger

logger = get_logger(__name__)


class SingletonBase:
    """
    A generic, thread-safe Singleton base class using the __new__ method.

    Subclasses inheriting from this will ensure only one instance of that
    specific subclass is created. Subclass __init__ methods should check
    the '_singleton_initialized' flag to perform initialization only once.
    """
    _instances = {}  # Dictionary to store instances keyed by class type
    _lock = threading.Lock()  # Lock for thread-safe instance creation

    def __new__(cls, *args, **kwargs):
        # Use double-checked locking for efficiency
        if cls not in cls._instances:  # First check (no lock)
            with cls._lock:  # Lock acquired only if instance might not exist
                # Second check (inside lock)
                if cls not in cls._instances:
                    logger.debug(f"Creating new Singleton instance for class {cls.__name__}")
                    # Create the new instance using the standard __new__
                    instance = super().__new__(cls)
                    # Store the instance in the class-specific dictionary
                    cls._instances[cls] = instance
                    # Add a flag to the instance to indicate it needs initialization
                    # This is done *before* __init__ is called automatically after __new__
                    instance._singleton_initialized = False
                # else: # Instance was created by another thread while waiting for lock
                #    logger.debug(f"Instance for {cls.__name__} already created by another thread.")
        # else: # Instance already exists
        #    logger.debug(f"Returning existing Singleton instance for class {cls.__name__}")

        return cls._instances[cls]
