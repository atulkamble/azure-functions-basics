```
// Azure Functions Project

git clone https://github.com/atulkamble/azure-functions-basics.git

// local run 

zip azure-functions-basics.zip function_app.py host.json requirements.txt local.settings.example.json
pip install -r requirements.txt
cp -n local.settings.example.json local.settings.json
func start

http://localhost:7071/api/hello

// azure deployment 

python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
func azure functionapp publish func-results-f6f3d744ee

// app live 

https://func-results-f6f3d744ee.azurewebsites.net/home


// check hello 

HELLO_KEY="$(az functionapp function keys list \
  --resource-group rg-func-results-f6f3d744ee \
  --name func-results-f6f3d744ee \
  --function-name Hello \
  --query default -o tsv)"

curl -i 'https://func-results-f6f3d744ee.azurewebsites.net/api/hello?name=Atul' \
  -H "x-functions-key: $HELLO_KEY"

unset HELLO_KEY

// Post Result 

RESULTS_KEY="$(az functionapp function keys list \
  --resource-group rg-func-results-f6f3d744ee \
  --name func-results-f6f3d744ee \
  --function-name CalculateResult \
  --query default -o tsv)"

curl -i -X POST \
  'https://func-results-f6f3d744ee.azurewebsites.net/api/results' \
  -H "x-functions-key: $RESULTS_KEY" \
  -H 'Content-Type: application/json' \
  --data '{"name":"Atul","marks":[80,70,90]}'

unset RESULTS_KEY
```
