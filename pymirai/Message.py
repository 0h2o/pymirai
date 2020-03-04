
def miraiPlain(text):
    return {'type':'Plain', 'text':text}

def miraiImage(image_id):
    return {'type':'Image', 'imageId':image_id}

def miraiAt(target, display):
    return {"type": "At", "target": target, "display": display}

def miraiAtAll():
    return {'type':'AtAll'}