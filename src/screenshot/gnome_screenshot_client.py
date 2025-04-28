"""
Screenshot client module for AnkiLive.

This module provides interfaces and implementations for capturing screenshots.
"""

import os
import tempfile
import subprocess
from abc import ABC, abstractmethod
from typing import Optional
import logging

from PIL import Image

from src.screenshot.screenshot_client import ScreenshotClient

# Configure logging
logger = logging.getLogger(__name__)


class GnomeScreenshotClient(ScreenshotClient):
    """Implementation of ScreenshotClient using gnome-screenshot."""
    
    def get_screenshot(self) -> Image.Image:
        """
        Capture a screenshot using gnome-screenshot and return it as a PIL Image.
        
        The user will be prompted to select an area of the screen to capture.
        
        Returns:
            PIL Image object containing the screenshot
            
        Raises:
            RuntimeError: If the screenshot capture fails
        """
        logger.info("Starting screenshot capture using gnome-screenshot")
        # Create a temporary file to store the screenshot
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name

        logger.debug(f"Temporary file created at {temp_path}")
            
        try:
            # Run gnome-screenshot with area selection (-a flag)
            logger.debug(f"Capturing screenshot to {temp_path}")
            subprocess.run(
                ['gnome-screenshot', '-a', '-f', temp_path])
            
            # Check if the file exists and has content
            if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                raise RuntimeError("Screenshot capture failed: Output file is empty or missing")
            
            # Open the image with PIL
            image = Image.open(temp_path)
            
            # Return a copy of the image to ensure it's still usable after the file is deleted
            return image.copy()
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Screenshot capture failed: {e.stderr.strip()}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except subprocess.TimeoutExpired:
            error_msg = "Screenshot capture timed out. Please try again."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Screenshot capture failed: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                logger.debug(f"Removed temporary file {temp_path}")