## URL Context - Google Gemini

### :zap: Resources
* Python
* genai - Google Generative AI
* PDFVectorizer
* PyPDF2
* langchain
* chromadb
<br>
<hr>

## Project Structure

```
flask-api-project
├── app
│   ├── __init__.py
│   └── query_rag.py
│   └── request_test.py
│   ├── routes.py
│   └── run_rag.py
├── requirements.txt
├── chroma_db
├── normativos
├── .env
├── config.py
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone git@github.com:me-wsantos/rag-flask-api.git
   cd rag-flask-api
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

5. Run script to vectorize files:
   ```
   python app/run_rag.py
   ```

## Running the API

To run the Flask API, use the following command:

```
flask run
```

Make sure to set the `FLASK_APP` environment variable to `app` before running the command.

## API Endpoint

- **POST /ask-rag**
  - Description: Receives a user question and returns a response.
  - Request Body: 
    ```json
    {
      "question": "Your question here"
    }
    ```
  - Response: 
    ```json
    {
      "answer": "The response to your question"
    }
    ```

### :technologist: Autor
<a href="https://github.com/me-wsantos">
<img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/179779189?v=4" width="100px;" alt=""/>
<br />
<p><b>Wellington Santos</b></sub></a> <a href="https://github.com/me-wsantos" title="GitHub"></a></p>