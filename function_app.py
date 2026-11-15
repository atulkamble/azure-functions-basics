import json
import logging

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


def json_response(data, status_code=200):
    return func.HttpResponse(
        json.dumps(data), status_code=status_code, mimetype="application/json"
    )


@app.function_name(name="Home")
@app.route(route="", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
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
    form { display:grid; gap:12px; margin-top:14px; }\n    label { display:grid; gap:5px; color:var(--ink); font-size:.92rem; font-weight:600; }\n    input { width:100%; border:1px solid #c7d4e2; border-radius:8px; padding:11px 12px; font:inherit; }\n    input:focus { outline:3px solid #0078d433; border-color:var(--blue); }\n    .marks { display:grid; grid-template-columns:repeat(3,1fr); gap:9px; }\n    button { width:max-content; border:0; border-radius:8px; background:var(--blue); color:white; padding:11px 16px; font:inherit; font-weight:700; cursor:pointer; }\n    button:disabled { opacity:.65; cursor:wait; }\n    .output { min-height:1.5em; color:var(--ink); white-space:pre-wrap; overflow-wrap:anywhere; }\n    .status { display:inline-flex; align-items:center; gap:8px; color:#176b3a; background:#eaf7ef; padding:6px 10px; border-radius:999px; font-size:.85rem; font-weight:650; }
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
        <p>Use the forms below. They call this Function App’s HTTP API directly.</p>
      </section>
      <section class="card">
        <h2>GET greeting</h2>
        <p>Enter a name to trigger the GET function.</p>
        <form id="hello-form">
          <label>Your name<input name="name" autocomplete="name" maxlength="80" required placeholder="Atul"></label>
          <button type="submit">Get greeting</button>
        </form>
        <p class="output" id="hello-output" role="status" aria-live="polite"></p>
        <p><code>GET /api/hello?name=Atul</code></p>
      </section>
      <section class="card">
        <h2>POST a result</h2>
        <p>Enter a student and three marks (0–100). Pass requires at least 40 in every subject.</p>
        <form id="results-form">
          <label>Student name<input name="name" autocomplete="name" maxlength="80" required placeholder="Atul"></label>
          <div class="marks">
            <label>Subject 1<input name="mark1" type="number" min="0" max="100" step="1" required value="80"></label>
            <label>Subject 2<input name="mark2" type="number" min="0" max="100" step="1" required value="70"></label>
            <label>Subject 3<input name="mark3" type="number" min="0" max="100" step="1" required value="90"></label>
          </div>
          <button type="submit">Calculate result</button>
        </form>
        <p class="output" id="results-output" role="status" aria-live="polite"></p>
        <p><code>POST /api/results</code></p>
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
  <script>
    const helloForm = document.querySelector("#hello-form");
    const resultsForm = document.querySelector("#results-form");

    helloForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const button = helloForm.querySelector("button");
      const output = document.querySelector("#hello-output");
      const name = new FormData(helloForm).get("name").trim();
      button.disabled = true;
      output.textContent = "Calling Azure Function…";
      try {
        const url = new URL("/api/hello", window.location.origin);
        url.searchParams.set("name", name);
        const response = await fetch(url);
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
        output.textContent = data.message;
      } catch (error) {
        output.textContent = error.message || "Could not reach the greeting function.";
      } finally {
        button.disabled = false;
      }
    });

    resultsForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const button = resultsForm.querySelector("button");
      const output = document.querySelector("#results-output");
      const form = new FormData(resultsForm);
      const payload = {
        name: form.get("name").trim(),
        marks: [form.get("mark1"), form.get("mark2"), form.get("mark3")].map(Number)
      };
      button.disabled = true;
      output.textContent = "Calculating with Azure Function…";
      try {
        const response = await fetch("/api/results", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
        output.textContent = `${data.name}: ${data.result} · ${data.percentage}% (${data.total}/${data.maximum})`;
      } catch (error) {
        output.textContent = error.message || "Could not reach the result function.";
      } finally {
        button.disabled = false;
      }
    });
  </script>
</body>
</html>""",
        status_code=200,
        mimetype="text/html",
    )


@app.function_name(name="Hello")
@app.route(route="api/hello", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def hello(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get("name", "").strip() or "Azure Functions"
    return json_response({"message": f"Hello, {name}!"})


@app.function_name(name="CalculateResult")
@app.route(route="api/results", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
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
