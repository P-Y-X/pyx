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

2. (Optional) You can add a boilerplate code for your model

    ```bash
    > cd <project_name>
    > pyx add <template_name>
    ```
    The command will create a model directory with the corresponding boilerplate code. You can run it locally:
    ```bash
    > cd models/<template_name>
    > python PYX.py
    ```

3. Modify the `PYX.py` script to reflect the logic of your model.
    * `PYX.py`

4. Run the local test to be sure everything is ready:
    ```bash
    > pyx test
    ```

5. Publish a model:
    ```bash
    > pyx publish
    ```

## Get a model from PYX cloud

Choose a model from the [PYX model shop](https://beta.pyx.ai/shop). If it is already available use pyx utility to download the model. 

```bash
pyx download <model_id>/<model_name>:revision
```

Where `model_id` could be found on the model's page. 
Then you can test the model locally:

```bash
cd <project_name>
pyx run <framework> <input_directory> <output_directory>
```

If model is not available yet you can buy it. Then it will be accessible for downloading.

## License

MIT
