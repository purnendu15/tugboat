
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

**-s / --spec PATH**

Path to excel spec, to be passed with generate_intermediary.

**-i / --intermediary**

Path to intermediary file, to be passed with generate_manifests.

**-S / --sitetype**
Specify site type, '5ec' or 'nc'. It is nc by default

**-h / --help**

Show the options and exit.

Usage:

::

    # Generate intermediary yaml and site manifests as separate steps
    ./tugboat.sh --excel <excel_file> --spec <excel_spec_file> --generate_intermediary
    ./tugboat.sh --intermediary <intermediary_file> --generate_manifests

    (OR)

    # Generate site manifests in a single command
    ./tugboat.sh --excel <excel_file> --spec <excel_spec_file> --generate_manifests

