import cv2
import easyocr
import numpy as np
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
import shutil

from constants import (PATH_IN, PATH_BTW, PATH_OUT, POPPLER_PATH)


def get_name_from_path(path: Path) -> str:
    """
    Extracts file name (w/o its extension) from the path
    :param path: file path
    :return: file name
    """
    return str(path).split('\\')[-1].split('.')[0]


class FileConverter:
    """
    PDF/JPEG Converter implementation
    """
    def __init__(self, poppler_path=None):
        self.poppler_path = poppler_path
        self.image_paths = []

    def jpg_to_pdf(self, path_in: Path, path_out: Path) -> None:
        """
        Converts multiple jpg-images to a single pdf-file
        :param path_in: jpg-images directory path
        :param path_out: pdf-file
        """
        images = [Image.open(file) for file in path_in.glob('*.jpg')]
        images[0].save(path_out, 'PDF', resolution=100.0, save_all=True, append_images=images[1:])

    def pdf_to_jpg(self, path_in: Path, path_out: Path) -> None:
        """
        Converts pdf-file to jpg-images and saves
        directory paths the images have been saved to
        :param path_in: pdf-file path
        :param path_out: path to create directory to store images of pdf-file pages
        """
        file_name = get_name_from_path(path_in)
        new_path_out = path_out / file_name
        if new_path_out.exists():
            shutil.rmtree(new_path_out)
        new_path_out.mkdir(parents=True)
        self.image_paths.append(new_path_out)

        pages = convert_from_path(path_in, 500, poppler_path=self.poppler_path)
        for count, page in enumerate(pages):
            page.save(new_path_out / f'{file_name}_{count}.jpg', 'JPEG')


class PreprocessedImage:
    """
    Preprocessed image abstraction
    """
    def __init__(self, image_path: Path,
                 binarize: bool = True, remove_noise: bool = False,
                 make_thin: bool = False, make_thick: bool = True):
        self._image_vector = np.array(Image.open(image_path))
        self._image_name = get_name_from_path(image_path) + '.jpg'

        if binarize:
            self._binarize()
        if remove_noise:
            self._remove_noise()
        if make_thin:
            self._make_thin()
        if make_thick:
            self._make_thick()

        cv2.imwrite(str(image_path), self._image_vector)

    def _binarize(self) -> None:
        """
        Converts the image to black and white
        """
        gray_image = cv2.cvtColor(self._image_vector, cv2.COLOR_BGR2GRAY)
        threshold, bw_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)
        self._image_vector = np.array(bw_image)

    def _remove_noise(self) -> None:
        """
        Removes noise from the image
        """
        kernel = np.ones((1, 1), np.uint8)
        image = cv2.dilate(self._image_vector, kernel, iterations=1)
        kernel = np.ones((1, 1), np.uint8)
        image = cv2.erode(image, kernel, iterations=1)
        image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        image = cv2.medianBlur(image, 3)
        self._image_vector = np.array(image)

    def _make_thin(self) -> None:
        """
        Makes font in the image thinner
        """
        image = cv2.bitwise_not(self._image_vector)
        kernel = np.ones((2, 2), np.uint8)
        image = cv2.erode(image, kernel, iterations=1)
        image = cv2.bitwise_not(image)
        self._image_vector = image

    def _make_thick(self) -> None:
        """
        Makes font in the image thicker
        """
        image = cv2.bitwise_not(self._image_vector)
        kernel = np.ones((5, 5), np.uint8)
        image = cv2.dilate(image, kernel, iterations=1)
        image = cv2.bitwise_not(image)
        self._image_vector = image


class TextRecognizer:
    """
    Extracts text from an image
    """
    def recognize_text(self, image_path: Path) -> list[str]:
        """
        Extracts text from the image
        :param image_path: image path
        :return: text recognized in the image
        """
        reader = easyocr.Reader(['ru'])
        return reader.readtext(str(image_path), detail=0, paragraph=True)
        # in this case allowlist didn't enhance the text recognition ability
        # allowlist='АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя-:"(!?.,;)0123456789I'


def main():
    CONVERTER = FileConverter(poppler_path=POPPLER_PATH)
    for file_path in PATH_IN.glob('*.pdf'):
        CONVERTER.pdf_to_jpg(file_path, PATH_BTW)
    images_paths = [path for path in CONVERTER.image_paths]

    RECOGNIZER = TextRecognizer()
    for images_path in images_paths:

        text_file_name = get_name_from_path(images_path)
        text_file_path = PATH_OUT / f'{text_file_name}.txt'
        with open(text_file_path, 'w', encoding='utf-8') as file:
            file_text = []

            for image_path in images_path.glob('*.jpg'):
                PreprocessedImage(image_path)
                text = RECOGNIZER.recognize_text(image_path)
                file_text.append(' '.join(text))
                file_text.append('\n')

            file_text = ' '.join(file_text)
            file.write(file_text)


if __name__ == '__main__':
    main()
