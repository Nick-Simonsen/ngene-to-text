Purpose
=======
Ngene-to-text provides a tool for converting Ngene DCE designs into Qualtrics-compatible text files for each implementation on the online survey platform. The code also includes a way to convert the resulting survey data into a friendly data analysis format.

# Example
```python
from ngene_to_text import NgeneProcessor

path = 'Ngene Example Output' # Path to Ngene designs

# Create an instance of the SurveyProcessor object
html_code = NgeneProcessor(directory_path = f'../{path}',
                           n_options = 2)

# Generate HTML code
html_code.process_ngene_designs()

# Save the HTML file as a TXT file
html_code.save_html_file(file_name = 'output',
      file_path = f'../{path}')
```