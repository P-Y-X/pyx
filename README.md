# PYX

## Installation

To install `pyx` locally, please run the following command:

```bash
pip install https://github.com/P-Y-X/pyx
```

## Publishing your model

1. To initialize a pyx project structure enter the project directory and run `create` command:

    ```bash
    cd <project_name>
    pyx create
    ```

    You will be ask to specify:
    * category of the project
    * project name
    * machine learning framework

    The command will create following files and directories:
    * `pyx.json`
    * `pyx-endpoints.py` the pyx integration and inference code
    * `pyx-web` directory for publishing on pyx platform 
    * `pyx-testing-data` directory for performing a local sanity check


3. Modify the `pyx-endpoints.py` script to reflect the logic of your model.
    You will need to implement two methods:
    1. `get_weight_paths()` should return the dict of weights paths
    2. `predict()` the inference code 

4. Run the local test to be sure everything is ready:
    ```bash
    pyx test
    ```

5. Publish and upload the model:
    ```bash
    pyx publish
    ```
    The code will pack and upload your model into pyx cloud. Then our team will verify the model. Once your model is verified your project will be available on the `pyx.shop`. 

Whenever you want to change a model information you can run:
```bash
pyx configure
```
and re-publish the model.

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
