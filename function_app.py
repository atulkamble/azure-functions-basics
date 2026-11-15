import json
import logging

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


def json_response(data, status_code=200):
    return func.HttpResponse(
        json.dumps(data), status_code=status_code, mimetype="application/json"
    )


@app.function_name(name="Home")
@app.route(route="/", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def home(req: func.HttpRequest) -> func.HttpResponse:
    """Serve a small public landing page at the Function App root."""
    return func.HttpResponse(
        body="""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#0078d4">
  <title>Student Result API | Azure Functions</title>
  <style>
    :root { color-scheme: light; --blue:#0078d4; --ink:#172b4d; --muted:#52657a; --line:#d9e2ec; --bg:#f3f7fb; }
    * { box-sizing:border-box; }
    body { margin:0; font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif; color:var(--ink); background:var(--bg); }
    header { background:linear-gradient(120deg,#063b70,#0078d4); color:white; padding:52px 22px 66px; }
    .wrap { width:min(960px,100% - 36px); margin:auto; }
    .eyebrow { text-transform:uppercase; letter-spacing:.13em; font-size:.76rem; font-weight:700; opacity:.82; }
    h1 { margin:.45rem 0; font-size:clamp(2rem,6vw,3.2rem); line-height:1.12; }
    header p { max-width:650px; color:#e8f4ff; margin:.8rem 0 0; font-size:1.08rem; }
    main { margin:-30px auto 50px; position:relative; }
    .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:18px; }
    .card { background:white; border:1px solid var(--line); border-radius:14px; padding:23px; box-shadow:0 8px 24px #17324d0d; }
    h2 { font-size:1.12rem; margin:0 0 12px; }
    p { margin:.4rem 0; color:var(--muted); }
    code, pre { font-family:ui-monospace,SFMono-Regular,Consolas,monospace; }
    code { color:#064f8c; background:#eef6fc; padding:.13rem .32rem; border-radius:5px; }
    pre { overflow:auto; background:#0e2238; color:#e7f2ff; padding:16px; border-radius:10px; font-size:.86rem; }
    .link { display:inline-block; margin:5px 9px 0 0; color:var(--blue); font-weight:650; text-decoration:none; }
    .link:hover { text-decoration:underline; }
    .status { display:inline-flex; align-items:center; gap:8px; color:#176b3a; background:#eaf7ef; padding:6px 10px; border-radius:999px; font-size:.85rem; font-weight:650; }
    .dot { width:8px; height:8px; background:#2e9d58; border-radius:50%; }
    footer { text-align:center; color:var(--muted); font-size:.88rem; padding:8px 18px 28px; }
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <div class="eyebrow">Microsoft Azure · Functions v4 · Python</div>
      <h1>Student Result API</h1>
      <p>A hands-on serverless learning project. Explore HTTP triggers, input validation, JSON responses, and Azure Functions deployment.</p>
    </div>
  </header>
  <main class="wrap">
    <div class="grid">
      <section class="card">
        <h2>Service status</h2>
        <p><span class="status"><span class="dot"></span>Function App is responding</span></p>
        <p>Try the greeting endpoint or send marks to calculate a student result.</p>
      </section>
      <section class="card">
        <h2>GET greeting</h2>
        <p>Optional query parameter: <code>name</code></p>
        <pre>GET /api/hello?name=Atul</pre>
        <a class="link" href="/api/hello?name=Atul">Try the endpoint →</a>
      </section>
      <section class="card">
        <h2>POST a result</h2>
        <p>Every mark must be an integer from 0 to 100. A pass requires at least 40 in each subject.</p>
        <pre>POST /api/results
Content-Type: application/json

{"name":"Atul","marks":[80,70,90]}</pre>
      </section>
      <section class="card">
        <h2>Learn and explore</h2>
        <p>Read the project guide and instructor delivery notes, or view the source.</p>
        <a class="link" href="https://github.com/atulkamble/azure-functions-basics">GitHub repository ↗</a>
        <a class="link" href="https://github.com/atulkamble/azure-functions-basics/blob/main/delivery.md">Teaching guide ↗</a>
      </section>
    </div>
  </main>
  <footer>Built with Azure Functions · Requests are calculated without storing student data.</footer>
</body>
</html>""",
        status_code=200,
        mimetype="text/html",
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
