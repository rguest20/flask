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
    'response': fields.String(default='')
}
parser = reqparse.RequestParser()
parser.add_argument('url')
parser.add_argument('id')
# parser.add_argument('api_key', required=True)

class ImageReturn(Resource):
    def get(self):
        data = parser.parse_args()
        url  = 'https://supremepetfoods.com/'
        id = 26715
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        response = requests.get(str(url) + 'wp-json/wp/v2/media/' + str(id), headers=headers)
        source_url = json.loads(response.content)['source_url']
        image_get = requests.get(source_url, headers=headers, stream=True)
        image = Image.open(BytesIO(image_get.content))
        filename = source_url.split('/')
        (x,y) = (image.size)
        if x > 1080 or y> 1080:
            image.thumbnail((1080,1080))
        image.save(filename[-1], optimize=True, quality=85)
        with open(filename[-1], "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            # url = data['url']
            # id = data['id']
            data['response'] = filename[-1]
            data['image64'] = encoded_string
        os.remove(filename[-1])
        return marshal(data, resource_fields)

api.add_resource(ImageReturn, '/')

if __name__ == '__main__':
    app.run(debug=True)
