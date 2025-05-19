from PIL import Image


class ResizeService:
    def resize(self, image: Image.Image, width: int, height: int) -> Image.Image:
        return image.resize((width, height))

    def resize_resize_image(
        self, image: Image.Image, width: int, height: int
    ) -> Image.Image:
        # Test line length: line-length = 88
        return self.resize(image, width, height)
