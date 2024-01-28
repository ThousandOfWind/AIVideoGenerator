import os

_current_dir = os.path.dirname(os.path.abspath(__file__))
getImageSearchQuery = os.path.join(_current_dir, "ImageSearchSystemMessageExample.json")
summaryNewsScript = os.path.join(_current_dir, "newsWebsiteToScript.json")
reviewGeneratedScripts = os.path.join(_current_dir, "reviewGeneratedScripts.json")
textToAnchorPrompt = os.path.join(_current_dir, "textToAnchor.json")
commonWebPageScript = os.path.join(_current_dir, "webpageToScript.json")
selectImageForCaption = os.path.join(_current_dir, "selectImageForCaption.json")
findTable = os.path.join(_current_dir, "summarizeTableInWebpage.json")