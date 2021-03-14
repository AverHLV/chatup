from io import BytesIO

from PIL import Image, ImageSequence


def resize_image(file: BytesIO, size: tuple) -> BytesIO:
    """ Resize image data depending on its extension """

    image = Image.open(file)
    ext = image.format
    resized_image_buffer = BytesIO()

    def _thumbnails(_frames, _size):
        for frame in _frames:
            thumbnail = frame.copy()
            thumbnail.thumbnail(_size, Image.ANTIALIAS)
            yield thumbnail

    if 'GIF' == ext:
        frames = ImageSequence.Iterator(image)
        frames = _thumbnails(frames, size)
        image = next(frames)
        image.save(resized_image_buffer, format=ext, save_all=True, append_images=list(frames), loop=0)
    else:
        image = image.resize(size)
        image.save(resized_image_buffer, format=ext)

    return resized_image_buffer
