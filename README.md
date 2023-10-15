# Text recognition algorithm
This is my implementation of a text recongition algorithm, or I'd rather say it's a try. 

To extract text from a pdf file, it first converts it into images, edits them (it's possible to choose in what way an image shall be filtered - black and white filter, noise removal, thinner/thicker text) and extracts the text into txt files.

Even though the algorithm doesn't recognize text in a good way, especially if handwritten text is passed, I found it useful to look into OCR field and work with according libraries, that's why I still wanna share my attempt to implement such an algorithm, despite it being not quite successful :) 

This task caught my interest, so as a perspective I see a possibility of retraining the easyocr model in order to make it recognize a Russian handwritten text by collecting a dataset and tuning the model's parameters (as suggested in [this video](https://youtu.be/-j3TbyceShY?si=yqcL-Wc5k1gIQpk_) and [this article](https://habr.com/ru/articles/691598/))
