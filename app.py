import json
import asyncio
import PIL
import os
import glob
import base64


from PIL import Image, ImageFile
from flask import Flask
from flask_restful import Resource, Api, reqparse, fields, marshal_with, marshal
import requests
from io import BytesIO
ImageFile.LOAD_TRUNCATED_IMAGES = True

app = Flask(__name__)
api = Api(app)

resource_fields = {
    'image64': fields.String(default='none'),
    'ext': fields.String(default='png')
}
parser = reqparse.RequestParser()
parser.add_argument('url', location='args')
parser.add_argument('id', location='args')
# parser.add_argument('api_key', required=True)

class ImageReturn(Resource):
    def get(self):
        data = parser.parse_args()
        url  = data['url']
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        source_url = url
        filename = source_url.split('/')[-1]
        image_get = requests.get(source_url, headers=headers, stream=True)
        image = Image.open(BytesIO(image_get.content))
        (x,y) = (image.size)
        if x > 1080 or y> 1080:
            image.thumbnail((1080,1080))
        image.save(filename, optimize=True, quality=85)
        with open(filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            # url = data['url']
            # id = data['id']
            data['image64'] = encoded_string.decode("utf-8")
        ext = os.path.splitext(filename)
        data['ext'] = ext[1]
        os.remove(filename)
        return marshal(data, resource_fields)

api.add_resource(ImageReturn, '/')

if __name__ == '__main__':
    app.run(debug=True)
