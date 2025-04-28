
from abc import ABC, abstractmethod
from PIL import Image


class ScreenshotClient(ABC):
    """Interface for screenshot clients."""
    
    @abstractmethod
    def get_screenshot(self) -> Image.Image:
        """
        Capture a screenshot and return it as a PIL Image.
        
        Returns:
            PIL Image object containing the screenshot
            
        Raises:
            RuntimeError: If the screenshot capture fails
        """
        pass

