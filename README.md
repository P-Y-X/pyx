# PYX

## Installation

To install `pyx` locally, please run the following command:

```bash
pip install https://github.com/P-Y-X/pyx
```

## Basic Usage

1. Initialize a project directory structure

    ```bash
    > pyx create
    ```

    You will specify:
    * category and subcategory of the project
    * project name
    * ml framework

    Then go to the project folder:
    ```bash
    > cd <project_name>
    ```

2. (Optional) You can add a boilerplate code for your model

    ```bash
    > pyx add <template_name>
    ```
    The command will create a model directory with the corresponding boilerplate code. You can run it locally:
    ```bash
    > cd models/<template_name>
    > python PYX.py
    ```

3. Modify the files to reflect the logic of your model.

    * `model.py`
    * `PYX.py`
    * `preprocessor.py`
    * `postprocessor.py`

4. Run the local test to be sure everything is ready:
    ```bash
    > pyx test
    ```

5. Publish a model:
    ```bash
    > pyx publish
    ```

## License

MIT.
