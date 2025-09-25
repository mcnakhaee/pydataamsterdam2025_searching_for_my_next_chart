# This file contains documentation specific to Chainlit, including setup instructions and usage examples.

# Chainlit Weaviate RAG Integration

## Overview

This project integrates Chainlit with a Weaviate-based Retrieval-Augmented Generation (RAG) program. It allows users to query a Weaviate database and receive generated responses based on the retrieved documents.

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd chainlit-weaviate-rag
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Copy the `.env.example` file to `.env` and fill in the required variables, such as:
   ```
   WEAVIATE_URL=<your-weaviate-instance-url>
   API_KEY=<your-api-key>
   ```

5. **Run the Application**
   ```bash
   chainlit run src/chainlit_app.py
   ```

## Usage Examples

- **Querying the RAG Program**
  After running the application, navigate to the provided URL in your browser. You can enter queries to retrieve relevant documents and generate responses based on them.

- **Customizing Prompts**
  Modify the prompt templates in `src/prompts/templates.py` to customize how the application generates responses based on user queries.

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes. Please ensure that your contributions adhere to the project's coding standards and include appropriate tests.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.