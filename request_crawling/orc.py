import easyocr

reader = easyocr.Reader(['ko', 'en'])
result = reader.readtext('./request_crawling/image.png')

for box, text, conf in result:
    print(text)