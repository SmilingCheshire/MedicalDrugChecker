import os
from flask import Flask, request, jsonify
import requests
import json
import yaml

# Load configuration at the top
def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

# Load config once
config_file = "config.yaml"
try:
    config = load_config(config_file)
    DESTINATION_OLLAMA_API = config['ollama']['api_url']
    BASE_PATH = config['ollama']['base_path']
    LLAMA_MODEL = config['llama']['model']
    FDA_API_BASE_URL = config['fda']['api_base_url']
except Exception as e:
    raise RuntimeError(f"Failed to load configuration: {str(e)}")

# Define the API endpoint
#FDA_API_BASE_URL = "https://api.fda.gov/drug/label.json"

app = Flask(__name__)

port = int(os.environ.get('PORT', 3000))

def get_medecine_ingredients(medicine_ids): 

    #Make request to the FDA open API
    #https://api.fda.gov/drug/label.json?search=id:5c5b1102-6baf-492a-ba2a-3d319c40283c+OR+id:ddf6e846-ebd0-4ed4-b151-914c4e39990e&limit=10
    
    try:
        # Prepare the FDA API query
        query = '+OR+'.join([f"id:{medicine_id}" for medicine_id in medicine_ids])
        fda_api_url = f"{FDA_API_BASE_URL}?search={query}&limit=10"

        # Make the API request to FDA
        response = requests.get(fda_api_url)

        # Check if the request was successful
        if response.status_code != 200:
            return {"error": "Failed to fetch data from FDA API.", "details": response.text}, 502

        # Parse the API response
        fda_data = response.json()
        results = fda_data.get("results", [])

        # Extract brand_name and substances_name
        medication_info = {}
        for item in results:
            brand_name = item.get("openfda", {}).get("brand_name", ["Unknown"])[0]
            substances = item.get("openfda", {}).get("substance_name", ["Unknown"])
            medication_info[brand_name] = substances

        return medication_info, 200

    except Exception as e:
        # Handle unexpected errors
        return {"error": "An unexpected error occurred.", "details": str(e)}, 500

@app.route("/")
def welcome():
    return "Hello!"

@app.route("/med_checker/search/<name>", methods=['GET'])
def search_medicine(name):
    # Search FDA open API
    # https://api.fda.gov/drug/label.json?search=aspirin
    
    if not name:
        return jsonify({"error": "Medicine name is required"}), 400    
   
    try:
    # sending get request and saving the response as response object
        response = requests.get(f"{FDA_API_BASE_URL}?search={name}")
        
        medicine_dic = {}
        
        data = response.json()
        for result in data.get("results", []):
            drug_id = result.get("id")
            brand_name = result.get("openfda", {}).get("brand_name", [])
            generic_name = result.get("openfda", {}).get("generic_name", [])
            active_ingredient = result.get("active_ingredient", [])
            purpose = result.get("purpose", [])
            manufacturer_name = result.get("openfda", {}).get("manufacturer_name", [])
            warnings =  result.get("warnings", [])
            route = result.get("openfda", {}).get("route", [])
            
            if drug_id:
                medicine_dic[drug_id] = {
                    "brand_name": brand_name,
                    "generic_name": generic_name,
                    "active_ingredient": active_ingredient,
                    "purpose": purpose,
                    "manufacturer_name": manufacturer_name,
                    "warnings": warnings,
                    "route": route
                }
        
        return medicine_dic
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500   

def makeRequest2Ollama(sSystemPrompt, sUserPrompt, sCotext):        
    
    # POST request to the Ollama dedicated server 
    # with input JSON parameters:
    # {
    #   "model": "llama3.1",
    #    "messages": [
    #       {
    #           "role": "system",
    #           "content": sSystemPrompt                
    #       },
    #       {
    #           "role": "user",    
    #           "content": sUserPrompt   
    #       }
    #   ],
    #   "context": sCotext,
    #   "stream": false         
    # }
    
    data = {'model': LLAMA_MODEL,
                'messages': [
                    {
                        'role': 'system',
                        'content': sSystemPrompt
                    },
                    {
                        'role': 'user',
                        'content': sUserPrompt        
                    }
                ],
                'context': sCotext,
                'stream': False 
            }
    
    json_data = json.dumps(data)
    
    try:
        response = requests.post(url=f"{DESTINATION_OLLAMA_API}{BASE_PATH}", data=json_data)
        
        # Parse the LLama response
        llm_response_dic = response.json()
        llm_message = llm_response_dic.get("message")
        result = llm_message.get("content")
        return result, 200
        
    except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500

@app.route("/med_checker/check", methods=['POST'])
def check_medications():    
    try:        
        # In the POST request paramenters there are JSON array with medications ID's; { "medicine_id" : ['ddf6e846-ebd0-4ed4-b151-914c4e39990e', '5c5b1102-6baf-492a-ba2a-3d319c40283c'] }
        data = request.get_json()  # Get the JSON data from the request
         # Validate JSON payload
        if not data or 'medicine_id' not in data or not isinstance(data['medicine_id'], list):
            return jsonify({"error": "Invalid input. 'medicine_id' must be a list."}), 400    
    
        # We should read these IDs in the loop and create a GET request to the FDA open API, for instance
        # https://api.fda.gov/drug/label.json?search=id:5c5b1102-6baf-492a-ba2a-3d319c40283c+OR+id:ddf6e846-ebd0-4ed4-b151-914c4e39990e&limit=10
        # We use for these purpouses the subroutine get_medecine_ingredients
    
        # Call the get_medecine_ingredients subroutine
        medication_info, status_code = get_medecine_ingredients(data['medicine_id'])    
    
        if status_code != 200:
            return jsonify(medication_info), status_code
    
        # in the response from the FDA open API we have to get ingredients and send tho the Ollama dedicated server, for example http://192.168.1.1/
        # with the prompt: 
        # You are a helpful, biochemical medicine expert. Based on the user request of the medicine ingredients give an expert answer:
        # limits answer by the severity of the interactions of the medicines ingredients. May be major, moderate, or minor.
    
        # minor: observe and adjust
        # description: These medications may interact in a clinically significant manner. However, the benefit of using these medications usually outweighs any risks. The medications may or may not require a dose adjustment and monitoring.

        # moderate: adjustment should be considered
        # description: The benefits of continuing the medication should be evaluated on an individual basis. Actions such as observing, changing the dose, or changing the medications may be considered.

        # major: combination should be avoided
        # description: This combination may cause more harm than benefit and alternative medications should be considered.
    
        # Answer should be prepared only in the JSON format. For example:
        # {'severity': 'minor', 'short_desc':'observe and adjust', 'description': 'These medications may interact in a clinically significant manner. However, the benefit of using these medications usually outweighs any risks. The medications may or may not require a dose adjustment and monitoring.'}
    
        # User prompt: from the return of the subroutine get_medecine_ingredients create user prompt
    
        # Make request to Ollama dedicated server via the makeRequest2Ollama subroutine
    
        #return jsonify({'success': True, 'severity': 'minor', 'short_description':'observe and adjust', 'description': 'These medications may interact in a clinically significant manner. However, the benefit of using these medications usually outweighs any risks. The medications may or may not require a dose adjustment and monitoring.'}), 200
    
        # Prepare the system and user prompts
        sSystemPrompt = (
            "You are a helpful, biochemical medicine expert. Based on the user request of the medicine ingredients, "
            "give an expert answer: limits answer by the severity of the interactions of the medicines ingredients. "
            "May be major, moderate, or minor. The answer must ALWAYS be in JSON format with the following structure:\n\n"
            "{\n"
            "    'severity': 'minor/moderate/major',\n"
            "    'short_desc': 'short description of the severity',\n"
            "    'description': 'detailed explanation of the severity'\n"
            "}.\n\n"
            "minor: observe and adjust\n"
            "description: These medications may interact in a clinically significant manner. However, the benefit of using "
            "these medications usually outweighs any risks. The medications may or may not require a dose adjustment and monitoring.\n\n"
            "moderate: adjustment should be considered\n"
            "description: The benefits of continuing the medication should be evaluated on an individual basis. Actions such as observing, "
            "changing the dose, or changing the medications may be considered.\n\n"
            "major: combination should be avoided\n"
            "description: This combination may cause more harm than benefit and alternative medications should be considered.\n\n"
            "You should not add additional comments, only JSON structure: { 'severity': 'minor/moderate/major', 'short_desc': 'short description of the severity', 'description': 'detailed explanation of the severity' }\n"
            "Examples: { 'severity': 'minor', 'short_desc': 'observe and adjust', 'description': 'These medications may interact in a clinically significant manner. However, the benefit of using these medications usually outweighs any risks. The medications may or may not require a dose adjustment and monitoring.' }\n"
            "{ 'severity': 'moderate', 'short_desc': 'adjustment should be considered', 'description': 'The benefits of continuing the medication should be evaluated on an individual basis. Actions such as observing, changing the dose, or changing the medications may be considered.' }\n"
            "{ 'severity': 'major', 'short_desc': 'combination should be avoided', 'description': 'This combination may cause more harm than benefit and alternative medications should be considered.' }"
        )

        sUserPrompt = (
            f"The following are the ingredients from the FDA API results: {medication_info}. "
            "Evaluate these based on their interactions."
        )

        # Prepare context
        sContext = (
            "Context: You are analyzing biochemical interactions of drug substances. "
            "Focus on clinical significance and categorize the severity of interactions as minor, moderate, or major."
        )
    
        # Call the Ollama server
        llm_response, llama_status_code = makeRequest2Ollama(sSystemPrompt, sUserPrompt, sContext)
    
        if llama_status_code != 200:
            return jsonify({"error": "Failed to process data with Ollama.", "details": llm_response}), llama_status_code
    
        # Parse and structure the response
        response_data = eval(llm_response)  # Evaluate JSON string to dictionary (ensure trusted source)

        # Return the structured response
        return jsonify({
            'success': True,
            'severity': response_data.get('severity', 'unknown'),
            'short_description': response_data.get('short_desc', 'No description available'),
            'description': response_data.get('description', 'No description available')
        }), 200
        
    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500    
    
if __name__ == '__main__':   
    
    app.run(host='0.0.0.0', port=port, debug=True)  
       