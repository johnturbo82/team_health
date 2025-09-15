# Team Health

## Installation

1. Clone the repository or download the files.
2. Copy `config.yaml.example` to `config.yaml` and set your own credentials.
3. Make sure Python and pip are installed.
4. Install the required dependencies with the following command:

```
pip install -r requirements.txt
```

## Running the Application for development

To start the application, run the following command:

```
python app.py
```

Then open your web browser and go to `http://127.0.0.1:5000` to use the application.

## Deploying via Docker

To deploy the application using Docker, follow these steps:

1. Copy `config.yaml.example` to `config.yaml` and set your own credentials.
2. `docker compose up -d` to build container and start the application.
3. **Access the application**:
   Open your web browser and go to `http://localhost:8000` to access the application.