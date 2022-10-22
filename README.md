# Amazon extractor

GUI extractor project with web scraping

## Convert ui file to py file:

pyuic5 -x .\gui_extractor.ui -o gui_extractor.py

## Run installer

pyinstaller --name "AmazonExtractor" --onefile --noconsole --icon="icons/app.ico" --add-data="icons;icons" --add-data="images;images" .\gui_main.py

