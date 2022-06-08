import cv2 as cv


def segments(filename):
    image = cv.imread(filename)
    if image is not None:
        original = image.copy()
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]

        # Morph close
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (7, 7))
        close = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernel, iterations=3)

        # Find contours and extract ROI
        cnts = cv.findContours(close, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        num = 0

        for c in cnts:
            x, y, w, h = cv.boundingRect(c)
            print(w, h)
            cv.rectangle(image, (x, y), (x + w, y + h), (36, 255, 12), 2)
            ROI = original[y : y + h, x : x + w]
            if w > 200 and h > 200:
                cv.imwrite("temp/images/seg_{}.png".format(num), ROI)
            num += 1

        return thresh
    else:
        return None
