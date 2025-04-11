# 📬 Gmail RAG Assistant

A Retrieval-Augmented Generation (RAG) pipeline that reads your Gmail inbox and sent items, stores the emails in a CSV file, and transforms them into embeddings using LangChain and FAISS for intelligent question-answering and analysis.


---

## 📑 Table of Contents

- [📂 Project Structure](#-project-structure)
- [📦 Required Libraries](#-required-libraries)
- [⚙️ Installation](#️-installation)
- [🚀 Usage](#-usage)
- [📄 Files](#-files)

---

## 📂 Project Structure

```plaintext
.
├── README.md
├── code
│   ├── data_request.py
│   ├── get_data.py
│   └── main.py
├── input
│   ├── emails.csv
│   └── emails_faiss_index
│       ├── index.faiss
│       └── index.pkl
└── secrets
    ├── client_secret.json
    └── token.json
```

---

## 📦 Required Libraries

Install these Python packages before running the code:

```bash
pip install pandas openai python-decouple faiss-cpu gradio matplotlib scikit-learn plotly
pip install --upgrade google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
pip install langchain langchain-openai
```

---

## ⚙️ Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/gmail-rag-assistant.git
   cd gmailrag
   ```

2. **Set Up the Environment**:
   - If using Conda:
     ```bash
     conda env create -f environment.yml
     conda activate llms
     ```
   - If using pip, manually install the packages listed in `environment.yml`.

---

## 🚀 Usage

1. **✅ Step 1: Check Gmail API Access**:
    Run this to verify Gmail API connectivity:
   ```bash
   python code/data_request.py
   ```

2. **📬 Step 2: Extract Emails**:
    This will fetch the most recent received and sent emails and store them in
    ```bash
    python code/get_data.py
    ```
3. **🧠 Step 3: Generate Embeddings and Create FAISS Index**:
    This will fetch the most recent received and sent emails and store them in
    ```bash
    python code/main.py
    ```

---

## 📄 Files

- `code/data_request.py`: Checks if the Gmail API connection is successful and if any emails exist.
- `code/get_data.py`: Connects to Gmail, fetches both inbox and sent messages, and saves them into a single CSV file.
- `code/main.py`: Loads emails from CSV, splits them, generates embeddings using LangChain and OpenAI, and saves them to a FAISS vector store.
- `input/emails.csv`: Combined list of received and sent Gmail emails.
- `input/emails_faiss_index`: Directory that contains the FAISS vector index created from the emails.
- `secrets/client_secret.json`: OAuth credentials for Gmail API access.
- `secrets/token.json`: OAuth access token generated after first-time login with Gmail..
---

