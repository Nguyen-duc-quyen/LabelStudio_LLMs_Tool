import cmd
import multiprocessing
import subprocess
import os
import yaml
import platform
import logging


def run_in_new_terminal(command: str):
    """
    Run a script in a new terminal window.
    """
    system = platform.system()
    if system == "Windows":
        subprocess.Popen(['start', 'cmd', '/k', command], shell=True)
    elif system == 'Darwin':  # macOS
        os.system(f'osascript -e \'tell app "Terminal" to do script "{command}"\'')
    elif system == 'Linux':
        subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'{command}; exec bash'])
    else:
        raise RuntimeError("Unsupported OS")


class MyApp():
    def __init__(self):
        # Setup logger
        # Logging to terrminal
        self.logger = logging.getLogger("DEAL LAB Label Studio LLM tool")
    
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        self.logger.propagate = False
        self.logger.setLevel(logging.INFO)


    def display_help(self):
        """
        Display help information.
        """
        self.logger.info("========================================== HELP ===================================")
        self.logger.info("1. Run the Label Studio server (Should be completed before running other functions)")
        self.logger.info("2. Run the LLM Query module")
        self.logger.info("3. Convert Exported JSON to readable format")
        self.logger.info("4. Help")
        self.logger.info("5. Exit")
        self.logger.info("===================================================================================")


    def run_label_studio(self):
        os.system("label-studio start")

        
    def run_llm_query(self):
        """
        Run the LLM Query module.
        """
        config_path = input("Please enter the path to the config file: ")
        command = f"python ./scripts/llm_query.py --config {config_path}"
        run_in_new_terminal(command)

    
    def convert_json(self):
        """
            Convert exported JSON to readable format.
        """
        input_json_path = input("Please enter the path to the exported JSON file: ")
        output_dir_path = input("Please enter the path to save the output Directory: ")
        run_in_new_terminal(f"python ./scripts/convert.py --input_json_path {input_json_path} --output_dir_path {output_dir_path}")


    def run(self):
        """
        Run the main loop of the application.
        """
        self.logger.info("Welcome to the DEAL Lab's Label Studio LLM pre-annotation tool!")
        self.display_help()
        while True:
            choice = input("Please enter your choice (1-5): ")
            if choice == "1":
                self.run_label_studio()
            elif choice == "2":
                self.run_llm_query()
            elif choice == "3":
                self.convert_json()
            elif choice == "4":
                self.display_help()
            elif choice == "5":
                self.logger.info("Exiting the application.")
                exit(0)
            else:
                self.logger.info("Invalid choice. Please try again.")
            

if __name__ == "__main__" :
    app = MyApp()
    app.run()