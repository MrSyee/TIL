import os

from PIL import Image


class ResizeService:
    """Something about `f`. And an example, Something about `f`. And an example:, Something about `f`. And an example.

    .. code-block:: python.

        foo, bar, quux = this_is_a_long_line(lion, hippo, lemur, bear)
    """

    def resize(self, image: Image.Image, width: int, height: int) -> Image.Image:
        """Test docstring."""
        os.environ["TEST"] = "test"
        return image.resize((width, height))

    def resize_resize_image(self, image: Image.Image, width: int, height: int) -> Image.Image:
        # Test line length: line-length = 100

        return self.resize(image, width, height)
