# Team Health

## Installation

1. Clone the repository or download the files.
2. Make sure Python and pip are installed.
3. Install the required dependencies with the following command:

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

1. **Build the Docker image**:
   Open a terminal and navigate to the root directory of your project. Run the following command to build the Docker image:

   ```sh
   docker build -t team_health_app .
   ```

2. **Run the Docker container**:
   After the image is built, run the following command to start a container from the image:

   ```sh
   docker run -d -p 8000:8000 team_health_app
   ```
   This command will start the container in detached mode (`-d`) and map port 8000 of the container to port 8000 on your host machine (`-p 8000:8000`).

3. **Access the application**:
   Open your web browser and go to `http://localhost:8000` to access the application.