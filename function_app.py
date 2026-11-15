import json
import logging

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


def json_response(data, status_code=200):
    return func.HttpResponse(
        json.dumps(data), status_code=status_code, mimetype="application/json"
    )


@app.function_name(name="Hello")
@app.route(route="hello", methods=["GET"])
def hello(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get("name", "").strip() or "Azure Functions"
    return json_response({"message": f"Hello, {name}!"})


@app.function_name(name="CalculateResult")
@app.route(route="results", methods=["POST"])
def calculate_result(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
    except ValueError:
        return json_response({"error": "Send a valid JSON object."}, 400)

    if not isinstance(data, dict):
        return json_response({"error": "Send a JSON object."}, 400)

    name = data.get("name")
    marks = data.get("marks")
    if not isinstance(name, str) or not name.strip():
        return json_response({"error": "name must be a non-empty string."}, 400)

    if not isinstance(marks, list) or not marks or any(
        type(mark) is not int or not 0 <= mark <= 100 for mark in marks
    ):
        return json_response(
            {"error": "marks must be a non-empty list of integers from 0 to 100."},
            400,
        )

    total = sum(marks)
    passed = all(mark >= 40 for mark in marks)
    logging.info("Calculated result for %d subjects", len(marks))
    return json_response({
        "name": name.strip(),
        "total": total,
        "maximum": 100 * len(marks),
        "percentage": round(total / len(marks), 2),
        "result": "Pass" if passed else "Fail",
    })
