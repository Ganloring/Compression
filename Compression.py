import os
from flask import Flask, request, jsonify, send_from_directory
from PIL import Image
import requests
import io
from flask_cors import CORS
import pillow_avif  # Have to import this before importing PIL
from PIL import Image

app = Flask(__name__)
CORS(app, resources={r"/compress": {"origins": "*"}})  # Autorise toutes les origines pour la route /compress
CORS(app, resources={r"/get_image": {"origins": "*"}})  # Autorise toutes les origines pour la route /compress

def compress_image(input_url, max_size):
    try:
        max_size = int(max_size)*1000
        # Téléchargez l'image depuis l'URL
        response = requests.get(input_url)
        img = Image.open(io.BytesIO(response.content))

        image_format = img.format

        # Calculez la nouvelle taille basée sur la taille maximale spécifiée
        width, height = img.size
        new_width = int(width)
        new_height = int(height)

        quality = 100
        avif_path = "avif_test.avif"
        img.save(avif_path, quality=quality, save_all=True)
        compressed_size = os.path.getsize(avif_path)

        while compressed_size > max_size:
            if(quality >= 1):
                img.save(avif_path, quality=quality, save_all=True)
                compressed_size = os.path.getsize(avif_path);
                quality -= 1
            else:
                break

        # Retournez les détails demandés
        return {
            "input_size": len(response.content),
            "output_size": compressed_size,
            "ancienne_dimensions": f"{width}x{height}",
            "nouvelles_dimensions": f"{new_width}x{new_height}",
            "input_format": image_format,
            "output_format": "AVIF",
            "output_url": "http://127.0.0.1:5000/get_image"
        }

    except Exception as e:
        print(f"Erreur lors de la compression : {str(e)}")
        raise

@app.route('/get_image')
def get_image():
    return send_from_directory("", "avif_test.avif");

@app.route('/compress', methods=['POST'])
def compress():
    try:
        data = request.get_json()
        input_url = data.get('input_url')
        max_size = data.get('max_size')

        result = compress_image(input_url, max_size)

        return jsonify(result)

    except Exception as e:
       print(f"Erreur lors de la compression : {str(e)}")
       return jsonify({"error": "Une erreur interne s'est produite lors de la compression"}), 500

if __name__ == '__main__':
    app.run(debug=True)
