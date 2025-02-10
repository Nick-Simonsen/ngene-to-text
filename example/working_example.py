from ngene_to_txt import NgeneProcessor, ImageConfig

#############
# Constants #
#############

# Change image configurations (width and height)
image_config = ImageConfig(width = 80, height = 72) # Change the width to 80px and height to 72px

# Dictionary for renaming attributes
attribute_renaming_dict = {
    'price': 'Price', # 'Original attribute name': 'New attribute name'
    'screen_size': 'Screen size',
    'processor': 'Processor',
    'ram': 'RAM',
    'storage_type': 'Storage type',
    'graphics_card': 'Graphics card',
    'warranty_period': 'Warranty period',
}

# Dict for renaming attributes levels
value_renaming_dict = {
    'price': {
        # Change the prices to include '$'
        # '800': '$800', # 'Original value': 'New value'
        '800': ('test', 'https://nottinghampsych.eu.qualtrics.com/ControlPanel/Graphic.php?IM=IM_fO2rnZxjQde5WR5'),
        '1,200': '$1,200',
        '1,500': '$1,500',
    },
    
    'screen_size': {
        '0': '13 inches',
        '1': '15 inches',
        '2': '17 inches',
    },

    'processor': {
        '0': 'Inten Core i5',
        '1': 'Intel Core i7',
        '2': 'AMD Ryzen 5',
        '3': 'AMD Ryzen 7',
    },

    'ram': {
        '0': '4GB',
        '1': '8GB',
        '2': '16GB',
        '3': '32GB',
    },

    'storage_type': {
        '0': 'HDD (500GB)',
        '1': 'HDD (1TB)',
        '2': 'SSD (256GB)',
        '3': 'SSD (512GB)',
    },

    'graphics_card': {
        '0': 'Intel UHD Graphics',
        '1': 'NVIDIA GeForce GTX 1650',
        '2': 'NVIDIA GeForce RTX 2060',
        '3': 'NVIDIA GeForce RTX 3080',
    },

    'warranty_period': {
        '0': '1 Year',
        '1': '3 Years',
        '2': '5 Years',
    },
}

# List of question texts for the choice questions, relevant paths, and task names
question_text = 'Among the following laptops, which one would you prefer to purchase?'
path = 'Ngene Example Output'
task_name = 'DCE Laptops'
opt_out_name = 'If these are the only options for laptops, I prefer not to purchase any at this time.'

######################################################################################
# Call relevant scripts for extracting, processing, and saving Ngene designs as HTML #
######################################################################################

# Create an instance of the SurveyProcessor object/Class
html_code = NgeneProcessor(directory_path = f'../{path}',
                           n_options = 2,
                           rename_attributes = attribute_renaming_dict,
                           rename_attribute_levels = value_renaming_dict,
                           task_name = task_name,
                           question_text = question_text,
                           opt_out = opt_out_name)

# Generate HTML code
html_code.process_ngene_designs()

# Save the HTML file
html_code.save_html_file(
    file_name = 'ngene_html_output',
    file_path = f'../'
)

###########################################################
# Load survey data and reformat into more readable format #
###########################################################
from ngene_to_txt import QualtricsSurveyDataProcessor
import pandas as pd

survey_data = pd.read_csv("../example_survey_data.csv", sep = ';')

# Known attributes I want to extract levels from
attributes = [
    "Price",
    "Screen size",
    "Processor",
    "RAM",
    "Storage type",
    "Graphics card",
    "Warranty period",
]

processed_data = QualtricsSurveyDataProcessor(data = survey_data,
                                 dce_attributes = attributes,
                                 task_name = task_name,
                                 opt_out = opt_out_name)

# Extract and save the survey data
processed_data.extract_survey_information().to_csv(f'../formatted_data.csv', index = False)
