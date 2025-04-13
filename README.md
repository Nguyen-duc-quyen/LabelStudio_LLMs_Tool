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
template: "./result_templates/project_4_result_template.json" # Prediction template file
```

## Usage
```
python main.py --config ./configs/chat_gpt_sample.yaml
```