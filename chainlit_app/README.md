# README.md

# Chainlit Weaviate RAG Project

This project is a simple web application built using Chainlit that integrates with a Weaviate-based Retrieval-Augmented Generation (RAG) program. It allows users to query a database of documents and receive relevant information in response.

## Overview

The Chainlit Weaviate RAG application leverages the capabilities of Weaviate to store and retrieve documents, while utilizing Chainlit to provide an interactive user interface. This setup enables efficient querying and information retrieval, making it suitable for various applications such as chatbots, knowledge bases, and more.

## Installation

To set up the project, follow these steps:

1. Clone the repository:

   ```
   git clone <repository-url>
   cd chainlit-weaviate-rag
   ```

2. Create a virtual environment (optional but recommended):

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables by copying the example file:

   ```
   cp .env.example .env
   ```

   Update the `.env` file with your specific configuration, including API keys and database URLs.

## Usage

To run the application, execute the following command:

```
python src/main.py
```

Once the application is running, you can access it in your web browser at `http://localhost:8000`.

## Project Structure

- `src/`: Contains the source code for the application.
  - `main.py`: Entry point for the Chainlit application.
  - `chainlit_app.py`: Main application logic and user interface.
  - `utils/`: Utility functions for various tasks.
  - `rag/`: Components related to the RAG program, including document loading and retrieval.
  - `models/`: Configuration for the language model.
  - `prompts/`: Prompt templates for generating queries.

- `data/documents/`: Directory for storing documents used by the RAG program.

- `.env.example`: Example environment variables file.

- `requirements.txt`: List of project dependencies.

- `chainlit.md`: Documentation specific to Chainlit.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.