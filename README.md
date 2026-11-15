# Azure Functions Basics

Build and deploy a **Student Result API** using **Python 3.11**, the **Python v2 programming model**, and **Azure Functions Flex Consumption**. Start with a GET endpoint, then use a POST endpoint to validate JSON and calculate a result.

## 1. Theory

| Concept | What it means |
|---|---|
| Serverless | Azure manages the infrastructure and scales the app. You write code that runs in response to events. |
| Function | One handler that runs when its trigger fires. This lab has two functions. |
| Function app | The Azure resource that groups functions for deployment and configuration. |
| Trigger | The event that starts a function. Each function has one trigger. |
| Binding | A declarative connection that supplies input or sends output, such as reading a blob or writing to a queue. The HTTP response is this lab's output. |
| Hosting plan | Determines scaling, compute and billing behavior. This lab uses Linux Flex Consumption with on-demand instances. |
| Cold start | A first request may take longer when Azure needs to start an instance. |
| Stateless code | A request should work on any instance. Store data in an external service when you need it to survive across requests. |
| Monitoring | Application Insights and Azure Monitor help inspect requests, logs and failures. |

| Trigger | Example |
|---|---|
| HTTP | Calculate a student result when a client sends JSON. |
| Timer | Run a daily summary job on a schedule. |
| Blob Storage | Process an uploaded document. |
| Queue Storage | Process a queued task in the background. |

**Version numbers:** Python 3.11 is the language version. Python v2 is the decorator-based programming model. Functions runtime v4 runs the app. The `"version": "2.0"` in `host.json` identifies the host configuration schema.

## 2. Project behavior

| Method and path | Azure function name | Behavior |
|---|---|---|
| GET `/api/hello?name=Atul` | `Hello` | Returns a JSON greeting. The name is optional. |
| POST `/api/results` | `CalculateResult` | Validates a student name and marks, then returns total, maximum, percentage and pass/fail. |

Each subject is out of 100. The student passes when **every subject scores at least 40**. Marks must be integers from 0 to 100. Percentage is the total divided by the number of subjects. The API calculates and returns each result without persisting it. The browser UI submits a greeting form to `/api/hello` and a marks form to `/api/results`; both calls execute the Azure Functions directly.

```text
azure-functions-basics/
├── function_app.py             # Complete source for both HTTP functions
├── host.json                  # Functions host settings
├── local.settings.example.json # Copy to local.settings.json before running
├── requirements.txt           # Python dependency
├── .funcignore                # Excludes local files from publish
├── .gitignore                 # Excludes local settings and environment from Git
└── README.md                  # This lab
```

In `function_app.py`, `@app.function_name` sets the Azure function name and `@app.route` declares the HTTP trigger, route and methods. The default route prefix is `/api`. The `json_response` helper serializes a Python dictionary and sets the response content type. Invalid input receives HTTP 400.

## 3. Install prerequisites

Run these commands in macOS Terminal with Homebrew installed. For Windows or Linux, use the [official Core Tools installation instructions](https://learn.microsoft.com/azure/azure-functions/functions-run-local).

```bash
brew install python@3.11 azure-cli
brew tap azure/functions
brew install azure-functions-core-tools@4

python3.11 --version
func --version
az version
```

Use Core Tools **4.x**. Azure deployment also needs an active subscription and permission to create resources in it. Azure usage can incur charges.

## 4. Run locally

In the directory containing the downloaded ZIP, extract it and enter the project root:

```bash
unzip azure-functions-basics.zip
cd azure-functions-basics
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp -n local.settings.example.json local.settings.json
func start
```

Keep this terminal running. Check that Core Tools lists both endpoints on port **7071**. This local HTTP-only lab leaves `AzureWebJobsStorage` blank. When you add storage-dependent triggers, configure Azurite or Azure Storage. The deployed Flex app uses the Azure Storage account you create below.

## 5. Test from a second terminal

```bash
BASE_URL="http://localhost:7071"
curl -i "$BASE_URL/api/hello?name=Atul"

curl -i "$BASE_URL/api/results" \
  -H 'Content-Type: application/json' \
  --data '{"name":"Atul","marks":[80,70,90]}'
```

Expected HTTP 200 responses:

```json
{"message":"Hello, Atul!"}
```

```json
{"name":"Atul","total":240,"maximum":300,"percentage":80.0,"result":"Pass"}
```

Try a valid failing score and invalid input:

```bash
curl -i "$BASE_URL/api/results" \
  -H 'Content-Type: application/json' \
  --data '{"name":"Atul","marks":[90,39,95]}'

curl -i "$BASE_URL/api/results" \
  -H 'Content-Type: application/json' \
  --data '{"name":"Atul","marks":[105]}'
```

The first request returns **200** with `"result":"Fail"`. The second returns **400** with a marks validation error. Repeat with malformed JSON such as `{bad json}` to check the JSON parsing error.

## 6. Create Azure resources and publish

Stop the local host with **Ctrl+C**. Use the project terminal and run each block in order.

```bash
az login
az account show --query '{subscription:name,id:id,tenant:tenantId}' -o table
az functionapp list-flexconsumption-locations -o table
```

If the displayed subscription differs from your lab subscription, select it with `az account set --subscription "YOUR_SUBSCRIPTION_ID"`. Set `LOCATION` to a supported region from the preceding output. The suffix keeps resource names unique. Reuse the same terminal so subsequent commands retain the variables.

```bash
LOCATION="eastus"
SUFFIX="$(python -c 'import secrets; print(secrets.token_hex(5))')"
RG="rg-func-results-$SUFFIX"
STORAGE="stresults$SUFFIX"
APP="func-results-$SUFFIX"

az group create --name "$RG" --location "$LOCATION"

az storage account create \
  --name "$STORAGE" --resource-group "$RG" --location "$LOCATION" \
  --sku Standard_LRS --kind StorageV2

az functionapp create \
  --name "$APP" --resource-group "$RG" --storage-account "$STORAGE" \
  --flexconsumption-location "$LOCATION" \
  --runtime python --runtime-version 3.11

func azure functionapp publish "$APP"
```

Wait for deployment success and check that the output lists `Hello` and `CalculateResult`. The publish command remotely installs the dependency from `requirements.txt`.

## 7. Test in Azure

The homepage and its two demo API routes are configured for **anonymous access** so the browser forms can call them directly without exposing a function key. These endpoints are publicly callable. The result route validates input and does not persist student data. If you change the routes back to `FUNCTION` authorization, browser forms will need a secure server-side proxy; never embed a function key in HTML or JavaScript.

```bash
APP_HOST="$(az functionapp show -g "$RG" -n "$APP" \
  --query defaultHostName -o tsv)"

HELLO_KEY="$(az functionapp function keys list -g "$RG" -n "$APP" \
  --function-name Hello --query default -o tsv)"

RESULTS_KEY="$(az functionapp function keys list -g "$RG" -n "$APP" \
  --function-name CalculateResult --query default -o tsv)"

curl -i "https://$APP_HOST/api/hello?name=Atul" \
  -H "x-functions-key: $HELLO_KEY"

curl -i "https://$APP_HOST/api/results" \
  -H "x-functions-key: $RESULTS_KEY" \
  -H 'Content-Type: application/json' \
  --data '{"name":"Atul","marks":[80,70,90]}'

unset HELLO_KEY RESULTS_KEY
```

Both requests should return HTTP 200. With the current anonymous route configuration, a browser or curl call works without a key. If you later restore `FUNCTION` authorization, use the function-key approach below and expect a keyless request to return HTTP 401. In Azure Portal, open your Function App and its Application Insights resource to inspect requests and traces. The app logs the number of subjects in each successful calculation.

### Test Azure APIs with curl

The current demo endpoints allow anonymous requests:

```bash
curl -i 'https://$APP_HOST/api/hello?name=Atul'

curl -i -X POST "https://$APP_HOST/api/results" \\
  -H 'Content-Type: application/json' \\
  --data '{"name":"Atul","marks":[80,70,90]}'
```

The homepage forms use these same APIs. The greeting form makes a GET request; the result form sends JSON with POST. Do not add function keys to the browser code.

## 8. Troubleshooting

| Symptom | Check |
|---|---|
| `func: command not found` | Check the Core Tools installation and open a new terminal. |
| `No job functions found` | Run from the directory with `host.json` and `function_app.py`. Activate `.venv`, install dependencies and read the first worker error. |
| Port 7071 already in use | Run `func start --port 7072` and use port 7072 in `BASE_URL`. |
| Azure returns 401 | Check that the key belongs to the function you are invoking and that the header contains the value. |
| Azure returns 404 | Check the actual host name, `/api` prefix, route and HTTP method. Verify the function appeared in the publish output. |
| Flex region rejected | Select a region listed by `az functionapp list-flexconsumption-locations`. |
| Azure deployment fails | Check the first error in the publish output. Confirm your selected subscription, permissions and Python runtime. |

## 9. Clean up

List the resources in the dedicated lab group before deleting it. The delete command removes **everything in that group**.

```bash
az resource list --resource-group "$RG" -o table
az group delete --name "$RG" --yes
az group exists --name "$RG"
```

The final command should print `false`.

## Microsoft Learn

- [Python developer reference](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [HTTP trigger and access keys](https://learn.microsoft.com/azure/azure-functions/functions-bindings-http-webhook-trigger)
- [Flex Consumption creation and management](https://learn.microsoft.com/azure/azure-functions/flex-consumption-how-to)
- [Create and deploy from the command line](https://learn.microsoft.com/azure/azure-functions/create-first-function-cli-python)
