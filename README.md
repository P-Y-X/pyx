# PYX

## Installation

To install `pyx` locally, please run the following command:

```bash
pip install https://github.com/P-Y-X/pyx
```

## Get a model from PYX cloud

Choose a model from the [pyx marketplace](https://beta.pyx.ai/models). 

First, authorize:
```bash
pyx auth <access_token>
```
You can find the `Access Token` on your pyx profile web page. 
Then pyx utility to download the model. 

```bash
pyx download <model_id>/<model_name>:revision
```

Where `model_id` could be found on the model's page. 
Then you can test the model locally:

```bash
cd <project_name>
pyx run <input_directory> <output_directory>
```

If model is not available yet you can buy it. Then it will be accessible for downloading.


## Publishing your own model

1. To initialize a pyx project structure enter the project directory and run `create` command:

    ```bash
    cd <project_name>
    pyx create
    ```

    Then follow the instructions. 

    The command will create these files and directories:
    * `pyx.json` the main pyx configuration file
    * `pyx-endpoints.py` the pyx integration and inference code
    * `pyx-web` directory for publishing on pyx platform 
    * `pyx-testing-data` directory for performing a local sanity check


3. Modify the `pyx_endpoints.py` script to reflect the logic of your model.
    You will need to implement two methods:
    1. `get_weight_paths()` should return the dict of weights paths
    2. `predict()` the inference code 

    **_NOTE:_** Model weights should be explicitly integrated into the model and be available locally. In-cloud containers have no internet access.


4. Run the local sanity test to be sure everything is ready:
    ```bash
    pyx test
    ```

5. If you passed the previous steps you can locally run your model to be sure it produces a proper result: 
    ```bash
    pyx run <input_dir> <output_dir>
    ```

    The `input_dir` should contain all the inputs required for the inference.
    The `output_dir` will contain the result after sucessful execution.


6. Publish and upload the model:
    ```bash
    pyx publish
    ```
    The code will pack and upload your model into the pyx cloud. Then our team will verify the model. Once your model is verified your project will be available on the [pyx marketplace](https://beta.pyx.ai/models). 

    **_NOTE:_** Be sure you have `requirements.txt` in the root directory and it contains all the dependencies. Right now we support only pip packages.

Whenever you want to change a model information you can run:
```bash
pyx configure
```

and re-publish the model:
```bash
pyx publish
```

## License

MIT
