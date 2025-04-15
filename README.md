# LabelStudio-LLMs Query Tool for the ShoeGen Project by DEAL Lab


## Descriptions
This tool is designed to assist annotators in generating attribute annotations for shoe images. It collects images for each LabelStudio project—either directly from the server or from the local machine—and queries the ChatGPT API to infer shoe attributes. The responses from ChatGPT are then automatically pushed to the LabelStudio server as **Predictions**.


## Installation
```
pip install -r requirements.txt
```

## Note
Your Label Studio server should be on before using the tool. For instructions on how to start the Label Studio server, check out the **Label-studio project setup** branch.


## Configuration
Modify the configuration in the ```./configs``` directory. The structure of the configuration file is as follow:
```
# Open AI configuration
openai_api_key: ""                                              # OpenAI API Key

# Label Studio configuration
label_studio_url: "http://localhost:8080"                       # Label Studio URL
label_studio_api_key: ""                                        # Label Studio Key (Each account has a separate key)
project_id: 4                                                   # Project ID (get from the server)
data_storage: "local"                                           # Data Storage mode "local" or "remote"
data_dir: ""                                                    # Data directory (for "local" mode only)
template: "./result_templates/project_4_result_template.json"   # Prediction template file

# Prompt configuration                                         
prompt: prompts.Prompt_1                                        # Specific prompt for generating predictions
model: gpt-4o                                                   # Model name (gpt-4o, fine-tuned model)
origin: ChatGPT-4o_baseline                                     # Value to keep track of the model origin used for predictions (baseline, fine-tunedv1, fine-tunedv2, etc.)
```

## Usage
Starting the tool in the terminal:
```
label-studio start
```

Generating predictions for a specific project based on the configuration file and pushing them to the Label Studio server:
```
python my_app.py
```
