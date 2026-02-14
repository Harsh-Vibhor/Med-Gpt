To run the app, use the following command:
python -m streamlit run app.py

After adding new pdf's, run the following command:
python ingest_documents.py

To setup the application, run the following command:
pip install -r requirements.txt 

To setup Ollama model:
1) Install Ollama from https://ollama.com/
2) Run the following command:
ollama serve
3) Install phi(oe other model) model by running the following command:
ollama pull phi 