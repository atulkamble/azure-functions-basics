# Azure Functions Basics

Build and deploy a **Student Result API** with Python 3.11, the Python v2 programming model, and Azure Functions runtime v4. The app includes two JSON API endpoints and a simple HTML landing page at the root URL.

## Endpoints

| Method and path | Function | Purpose | Authorization |
|---|---|---|---|
| GET `/` | `Home` | Project landing page | Anonymous |
| GET `/api/hello?name=Atul` | `Hello` | Greeting JSON | Function key in Azure |
| POST `/api/results` | `CalculateResult` | Validate marks and calculate result | Function key in Azure |

The root page is intentionally public. The two API endpoints use the app's default Function authorization. Each subject is out of 100; the student passes if every mark is at least 40. Requests are calculated in memory and are not persisted.

## Runtime requirements

The Function App is configured for **Python 3.11**. Use Python 3.11 locally when creating the virtual environment and publishing. A different local interpreter can produce package/runtime mismatches. The deployment log showed local Python 3.14.3 while the app expects 3.11; that warning did not stop upload, but use a matching interpreter for reliable builds.

### macOS with Homebrew

```bash
brew install python@3.11 azure-cli
brew tap azure/functions
brew install azure-functions-core-tools@4

python3.11 --version
func --version
```

From the repository root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
func start
```

Core Tools should list **Home**, **Hello**, and **CalculateResult**. Check the homepage locally at `http://localhost:7071/` and the API at `http://localhost:7071/api/hello?name=Atul`.

## Publish the existing Azure Function App

Sign in to the correct subscription and confirm the target app before publishing:

```bash
az login
az account show --query '{subscription:name,id:id}' -o table
az functionapp show --name func-results-f6f3d744ee --resource-group rg-func-results-f6f3d744ee --query '{name:name,state:state,host:defaultHostName}' -o table
```

Activate the Python 3.11 environment, then publish:

```bash
source .venv/bin/activate
python --version
func azure functionapp publish func-results-f6f3d744ee
```

The publish output should list **Home**, **Hello**, and **CalculateResult**. If it lists only the latter two, the deployed package did not discover the root function; inspect the first Python worker error in deployment logs before continuing.

Then check the public homepage and greeting endpoint:

```bash
curl -i https://func-results-f6f3d744ee.azurewebsites.net/
curl -i 'https://func-results-f6f3d744ee.azurewebsites.net/api/hello?name=Atul'
```

The API routes require a function key in Azure. Retrieve it without printing it into shared logs:

```bash
HELLO_KEY="$(az functionapp function keys list \
  --resource-group rg-func-results-f6f3d744ee \
  --name func-results-f6f3d744ee \
  --function-name Hello --query default -o tsv)"

curl -i 'https://func-results-f6f3d744ee.azurewebsites.net/api/hello?name=Atul' \
  -H "x-functions-key: $HELLO_KEY"
unset HELLO_KEY
```

## Verify result calculation

Local test:

```bash
curl -i http://localhost:7071/api/results \
  -H 'Content-Type: application/json' \
  --data '{"name":"Atul","marks":[80,70,90]}'
```

Expected response:

```json
{"name":"Atul","total":240,"maximum":300,"percentage":80.0,"result":"Pass"}
```

For Azure, call the same path and include the `CalculateResult` function key in the `x-functions-key` header.

## Why the default Azure welcome page may still appear

The Functions host's built-in welcome page appears when there is no function route handling `/`. Check these items:

1. Confirm the deployment output lists `Home - [httpTrigger]`.
2. Open the URL with the trailing slash: `https://func-results-f6f3d744ee.azurewebsites.net/`.
3. If Home is listed but the old page remains, wait briefly for the host to restart, then refresh without cache.
4. If Home is missing, verify `function_app.py` was published from the repository root and that Core Tools is running in the Python 3.11 virtual environment.

## Teaching guide

See [delivery.md](delivery.md) for the 75-minute instructor script, diagrams, explanations, and learner questions.
