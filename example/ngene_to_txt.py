from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
import pandas as pd
import os
import re


class ImageConfig:
    def __init__(self, width: int = 20, height: int = 18) -> None:
        self.width = str(width)
        self.height = str(height)


class NgeneProcessor:
    def __init__(self, directory_path: str, n_options: int,
                 rename_attributes: Dict[str, str] = None,
                 rename_attribute_levels: Dict[str, Dict[str, str]] = None,
                 task_name: str = "DCE", question_text: str = "",
                 opt_out: str = "") -> None:
        
        self.directory_path = directory_path
        self.n_options = n_options
        self.rename_attributes = rename_attributes or {}
        self.rename_attribute_levels = defaultdict(dict, rename_attribute_levels or {})
        self.task_name = task_name
        self.question_text = question_text
        self.opt_out = opt_out
        self.unwanted_attributes = ['', 'Choice question:']
        self.image_config = ImageConfig()
        self.generated_html_code = []
    """
    A class used to process Ngene designs.

    This class takes a directory path and number of options as input, and processes all the HTML files in the directory.
    The HTML files are parsed and HTML code is generated for each file. The HTML code is based on the attribute-value pairs
    in the table present in the HTML file. The attribute names and values can be renamed based on the provided dictionaries.

    Attributes:
        directory_path (str): The path to the directory containing the HTML files.
        n_options (int): The number of options in the DCE.
        rename_attributes (Dict[str, str], optional): A dictionary mapping old attribute names to new ones.
        rename_attribute_levels (Dict[str, Dict[str, str]], optional): A dictionary mapping old attribute level names to new ones.
        task_name (str, optional): The name of the task. Defaults to 'DCE'.
        question_text (str, optional): The text of the question. Defaults to an empty string.
        opt_out (str, optional): The opt-out option. Defaults to an empty string.
        unwanted_attributes (List[str]): A list of attribute names that should be ignored.
        image_config (ImageConfig): An object containing the configuration for the images.
        generated_html_code (List[str]): A list containing the generated HTML code.
    """

    def process_ngene_designs(self) -> List[str]:
        """
        Processes the Ngene designs in the directory specified during the object initialization.

        This method reads all the HTML files in the directory, parses them using BeautifulSoup, 
        and creates HTML code for each file. The HTML code is created based on the attribute-value 
        pairs in the table present in the HTML file. The attribute names and values are renamed 
        based on the rename_attributes and rename_attribute_levels dictionaries if they are present 
        in them. 

        Returns:
            list: A string list containing the generated HTML
        """
        
        html_code = [
            self._create_html(
                {
                    self.rename_attributes.get(attribute, attribute): [
                        self.rename_attribute_levels[attribute].get(value, value) 
                        for value in (cell.text.strip() for cell in row.find_all('td')[1:])
                    ]
                    for row in BeautifulSoup(Path(html_file_path).read_text(), 'html.parser').find('table').find_all('tr')
                    if (attribute := row.find_all('td')[0].text.strip()) not in self.unwanted_attributes
                },
                i
            )
            for i, html_file_path in enumerate(Path(self.directory_path).glob('*.html'), start = 1)
        ]

        self.generated_html_code = html_code

    def _create_html(self, data: Dict[str, Dict[str, str]], task_id: int) -> str:
        """
        Wraps Ngene designs in HTML code

        Args:
            data (Dict[str, Dict[str, str]]): A dictionary mapping attribute names to their values.
            task_id (int): The ID of the task.

        Returns:
            str: The generated HTML code as a string.
        """

        def _create_cell(option, value = None, is_header = False):
            style = ("width:270px; text-align: center; border-left: 4px solid black; "
                     "border-top: 4px solid black; border-right: 4px solid black; border-bottom: 1px solid black;")
            if isinstance(value, (tuple, list)):
                name, link = value
                content = f'<span hidden>{name}</span><img style="width: {self.image_config.width}px; height: {self.image_config.height}px;" src="{link}" data-image-state="ready">'
            else:
                content = f"<strong>Option {option}</strong>" if is_header else value
            return f'<td bgcolor="white" style="{style}">{content}</td>\n'

        html_parts = [
            f'[[AdvancedFormat]]\n[[Block:{self.task_name}]]\n' if task_id == 1 else "",
            f'[[Question:Matrix]]\n[[ID:{self.task_name}{task_id}]]\n',
            f'''
            {self.question_text} </br >
            <br />
            <style type="text/css">
            table {{
                border: none;
                border-collapse: collapse;
            }}
            th, td {{
                padding: 5px;
            }}
            th {{
                text-align: left;
            }}
            td:first-child {{
                border-left: none;
                border-top: none;
            }}
            </style>
            <table>
            <tbody>
            <tr>
            <td style="width:180px; border-bottom: 1px solid black;">&nbsp;</td>
            ''',
            ''.join(_create_cell(option, is_header = True) for option in range(1, self.n_options + 1)),
            '</tr>',
            ''.join(
                f'<tr>\n<td height="100" style="text-align: left; border-bottom: 1px solid black;"><strong>{attribute}</strong></td>\n' +
                ''.join(_create_cell(option, value) for option, value in enumerate(values, start = 1)) +
                '</tr>\n'
                for attribute, values in data.items()
            ),
            '''
            </tbody>
            </table>
            [[Choices]]
            Your choice:
            [[AdvancedAnswers]]
            ''',
            ''.join(f'[[Answer]]\nOption {option}\n' for option in range(1, self.n_options + 1)),
            f'[[Answer]]\n{self.opt_out}\n' if self.opt_out else "",
            '[[PageBreak]]\n'
        ]

        return ''.join(html_parts)


    def save_html_file(self, file_name: str, file_path: str) -> None:
        with open(os.path.join(file_path, file_name + '.txt'), 'w', encoding = 'utf-8') as f:
            f.write(''.join(self.generated_html_code))


class QualtricsSurveyDataProcessor:
    def __init__(self, data: pd.DataFrame, dce_attributes: List[str], task_name: str = "DCE",
                 PID_col: str = 'PID', opt_out: str = "Opt-out Option") -> None:
        self.data = data
        self.task_name = task_name
        self.dce_attributes = dce_attributes
        self.PID_col = PID_col
        self.opt_out = opt_out

    """
    A class used to process survey data from Qualtrics

    This class takes a DataFrame and a list of DCE attributes as input, and processes the DataFrame to extract and
    format DCE information. The extracted and formatted DCE information is returned as a DataFrame.

    Attributes:
        data (pd.DataFrame): The DataFrame containing the survey data.
        dce_attributes (List[str]): The list of DCE attributes.
        task_name (str, optional): The string used to identify columns related to DCE designs. Defaults to 'DCE'.
        PID_col (str, optional): The name of the column containing participant IDs. Defaults to 'PID'.
        opt_out (str, optional): The string used to identify opt-out choices. Defaults to 'Opt-out Option'.
    """

    
    def extract_survey_information(self) -> pd.DataFrame:
        """
        Extracts information from a DataFrame based on specified DCE attributes specified during object initialization.

        This function iterates over each row in the DataFrame, and for each column that contains the DCE string,
        it extracts the choice made by the participant and the levels of each DCE attribute. The extracted information
        is then stored in a dictionary and appended to a list.

        This function calls the format_data method to format the extracted information into a DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing the formatted DCE information. Each row corresponds to a choice made by a
                participant, and the columns correspond to the participant ID, task, alternative, attribute levels, and choice made.
        """

        extracted_information = []
        columns_to_check = [col for col in self.data.columns if self.task_name in col]
        dce_attributes_set = set(self.dce_attributes)

        large_strings = {column_name: self.data[column_name].iloc[0].strip().split('\n') for column_name in columns_to_check}

        # TO-DO: Implement way of checking if first two rows exists and if not, handle in some way
        for i, row in self.data.iloc[2:].iterrows(): # Skip the first two rows (Qualtrics irrelevant information)
            for column_name in columns_to_check:
                large_string = large_strings[column_name]
                choice_made = row[column_name]

                if pd.isna(choice_made):
                    continue

                levels = {attr: [] for attr in self.dce_attributes}
                current_attribute = None
                for line in large_string:
                    line = line.strip()
                    if line in dce_attributes_set:
                        current_attribute = line
                    elif current_attribute and line != '':
                        line = line.replace("- Your choice:", "").strip()
                        levels[current_attribute].append(line)

                levels = {attribute: level for attribute, level in levels.items() if level}

                extracted_information.append({
                    "PID": row[self.PID_col],
                    "Column": column_name,
                    "Choice made": choice_made,
                    "Attribute levels": levels
                })
        
        return self.format_data(extracted_information)


    def format_data(self, extracted_information: pd.DataFrame) -> pd.DataFrame:
        """
        Formats the extracted DCE information into a DataFrame.

        This function iterates over the extracted information, which is a list of dictionaries. 
        For each dictionary, it extracts the task name, choice made, attribute levels, and participant ID. 
        If "Choice made" contains the opt-out string, it sets the 'Choice' field to -1 for all alternatives. 
        It then formats this information into a dictionary, which is appended to a list. 
        This list is then converted into a DataFrame.

        Args:
            extracted_information (pd.DataFrame): A DataFrame containing the extracted DCE information.

        Returns:
            pd.DataFrame: A DataFrame containing the formatted DCE information. Each row corresponds to a choice made by a
                participant, and the columns correspond to the participant ID, task, alternative, attribute levels, and choice made.
        """

        task_splitter = re.compile(r'(\D)(\d)')
        
        extracted_data = []
        for info in extracted_information:
            max_alt = max(len(levels) for levels in info["Attribute levels"].values())
            for i in range(max_alt):
                extracted_data.append({
                    **{'Task': task_splitter.sub(r'\1 \2', info["Column"].split('_')[0]), 'PID': info["PID"], 'Alt': i+1},
                    **{attribute: levels[i] if i < len(levels) else '0' for attribute, levels in info["Attribute levels"].items()},
                    **{'Choice': 1 if info["Choice made"] == f"Option {i+1}" else 0}
                })
            # Add additional row for opt-out alternative
            opt_out_choice = 1 if self.opt_out in info["Choice made"] else 0
            extracted_data.append({
                **{'Task': task_splitter.sub(r'\1 \2', info["Column"].split('_')[0]), 'PID': info["PID"], 'Alt': max_alt + 1},
                **{attribute: '0' for attribute in info["Attribute levels"].keys()},
                **{'Choice': opt_out_choice}
            })

        return pd.DataFrame(extracted_data)

