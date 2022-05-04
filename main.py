import uuid

from flask import abort, Flask, make_response, render_template, request
import cv2
import numpy as np

ADD = "add"
MULTIPLY = "multiply"


app = Flask(__name__)

IMAGES = {}



@app.get("/")
def home_page():
    return render_template("home.html.j2")


@app.post("/")
def perform_operation():
    try:
        factors = [float(x) for x in request.form["fact"].split(",")]
        sums = [int(x) for x in request.form["sum"].split(",")]
        print(factors, sums)
        data = request.files["file"].read()
        if not data:
            return "no file selected"
        data_arr = np.frombuffer(data, dtype=np.uint8)
        img = cv2.imdecode(data_arr, cv2.IMREAD_COLOR)
    except KeyError:
        return "missing parameters :("
        
    identiifer = uuid.uuid4()
    output_images = make_output_images(img, factors=factors, sums=sums)
    IMAGES.update({
        f"{identiifer}-{key}-{idx}": inner_val
        for key, value in output_images.items()
        for idx, inner_val in enumerate(value)
    })
    return render_template(
        "output.html.j2",
        output_images={
            key: f"/img/{identiifer}-{key}"
            for key in output_images
        }
    )


@app.get("/img/<identifier>")
def get_hosted_image(identifier):
    try:
        retval, buffer = cv2.imencode('.png', IMAGES[identifier])
        resp = make_response(buffer.tobytes())
        resp.mimetype = "image/png"
        return resp
    except KeyError:
        abort(404)

def make_output_images(img, factors=(), sums=()):
    imgs = {}
    # imgs["original"] = img
    for factor in factors:
        imgs[f"factor_{factor}"] = [
            make_image(img, MULTIPLY, factor, clip)
            for clip in (False, True)
        ]
    for sum_ in sums:
        imgs[f"sum_{sum_}"] = [
            make_image(img, ADD, sum_, clip)
            for clip in (False, True)
        ]
    return imgs


def make_image(img, operation, operand, clip=False):
    if operation == ADD:
        new_img = img + operand
        if clip:
            new_img[img>255-operand] = 255
            new_img[img+operand<0] = 0
    elif operation == MULTIPLY:
        new_img = img * operand
        if clip:
            new_img[img>255/operand] = 255
            new_img[img*operand<0] = 0
    else:
        raise RuntimeError("unknown operation")
    return new_img


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
