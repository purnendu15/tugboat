
What is Tugboat?
----------------

Tugboat is a tool to generate Airship site manifest files from an excel
based engineering spec. The tool accepts Excel sheet and corresponding
excel specification as inputs and generates the site level manifests. As
an optional step it can generate an intermediary yaml which contain all
the information that will be rendered to generate Airship site manifests.
This optional step will help the deployment engineer to modify any data
if required.

Basic Usage
-----------

Before using Tugboat, you must:

1. Clone the Tugboat repository:

     git clone https://github.com/att-comdev/tugboat

2. Install the required packages in tugboat/:

     pip3 install -r tugboat/requirements.txt
3. Preparation 

   Step1:
   customize excel_spec.yaml based design specification.
   A sample is kept at tugboat/samples/specs/excel_spec.yaml.
   Please correctly specify the cell and coulmn numbers by referrring the desing spec

   Step2:
   Edit tugboat/tugboat/config/rules.yaml based on project settings.
   These are values which are not present in design spec.

4. To run the tool:

    export WORKSPACE=<dir where excelspecs are placed>
    export IMAGE=<docker_image>
    tugboat/tools/tugboat.sh <command> <options>

CLI Options
-----------


**-g / --generate_intermediary**

Generate intermediary file from passed excel and excel spec.

**-m / --generate_manifests**

Generate manifests from the generated intermediary file

**-x / --excel PATH**

Path to engineering excel file, to be passed with generate_intermediary.
One can specify multiple files here for example:  -x <file1> -x<file2>

**-s / --spec PATH**

Path to excel spec. To be passed with generate_intermediary.
The excel spec specifies worksheet and specific cells to refer
for data extraction from a engineering  excel file. When using
multiple such files, one can specify filename:sheetname in 
excel spec to identify specifc sections depending upon the
file name. 

**-i / --intermediary**

Path to intermediary file, to be passed with generate_manifests.

**-d / --site_config**
Site specific configurations


**-l / --loglevel**
Specify log-level.Loglevel NOTSET:0 ,DEBUG:10,    INFO:20,
WARNING:30, ERROR:40, CRITICAL:50  [default:20]

**-h / --help**

Show the options and exit.

Usage:

::


    # Generate intermediary yaml and site manifests as single step
    tugboat --generate_intermediary --generate_manifests --excel <file> --spec <excel_spec_file>  --site_config <site_cfg>


    # Generate intermediary yaml and site manifests as separate steps
    tugboat --generate_intermediary --excel <excel_file> --spec <excel_spec_file>  --site_config <site_config_file>
    tugboat --intermediary <intermediary_file> --generate_manifests

    (OR)

    # Generate intermediary yaml only
    tugboat --generate_intermediary --excel <file> --spec <excel_spec_file>  --site_config <site_cfg>

