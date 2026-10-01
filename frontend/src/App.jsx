import { useEffect, useState } from "react";

const API = "http://localhost:8000/api";

function App() {
  const [files, setFiles] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [topK, setTopK] = useState(5);

  async function loadDocuments() {
    const response = await fetch(`${API}/documents`);
    const data = await response.json();
    setDocuments(data.documents || []);
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  async function uploadFiles() {
    if (!files.length) return;

    setUploading(true);
    const formData = new FormData();

    for (const file of files) {
      formData.append("files", file);
    }

    try {
      const response = await fetch(`${API}/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      alert(data.message);
      setFiles([]);
      await loadDocuments();
    } catch (error) {
      alert(error.message);
    } finally {
      setUploading(false);
    }
  }

  async function askQuestion(event) {
    event?.preventDefault();

    if (!question.trim()) return;

    setLoading(true);
    setAnswer(null);

    try {
      const response = await fetch(`${API}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
          top_k: topK,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Question failed");
      }

      setAnswer(data);
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="hero">
        <div>
          <p className="eyebrow">SEMANTIC SEARCH + GROUNDED ANSWERS</p>
          <h1>TechDoc RAG</h1>
          <p className="subtitle">
            Upload technical documentation and ask questions using your own
            knowledge base.
          </p>
        </div>

        <div className="architecture">
          <span>Documents</span>
          <b>→</b>
          <span>Chunks</span>
          <b>→</b>
          <span>Embeddings</span>
          <b>→</b>
          <span>Top-K</span>
          <b>→</b>
          <span>Answer</span>
        </div>
      </header>

      <main className="grid">
        <aside className="panel">
          <h2>1. Add documentation</h2>

          <label className="dropzone">
            <input
              type="file"
              multiple
              accept=".pdf,.md,.txt"
              onChange={(e) => setFiles(Array.from(e.target.files))}
            />
            <strong>Choose files</strong>
            <span>PDF, Markdown or TXT</span>
          </label>

          {files.length > 0 && (
            <div className="file-list">
              {files.map((file) => (
                <div className="file-row" key={file.name}>
                  <span>{file.name}</span>
                  <small>{Math.round(file.size / 1024)} KB</small>
                </div>
              ))}
            </div>
          )}

          <button
            className="primary"
            onClick={uploadFiles}
            disabled={uploading || !files.length}
          >
            {uploading ? "Indexing..." : "Upload & Index"}
          </button>

          <h3>Indexed documents</h3>
          {documents.length === 0 ? (
            <p className="muted">No documents yet.</p>
          ) : (
            <ul className="documents">
              {documents.map((doc) => (
                <li key={doc}>📄 {doc}</li>
              ))}
            </ul>
          )}

          <div className="feature-box">
            <strong>Extra feature</strong>
            <p>
              The system checks retrieval confidence before generating an
              answer. If the question isn't supported by your documents, it
              refuses to guess.
            </p>
          </div>
        </aside>

        <section className="panel chat-panel">
          <div className="chat-header">
            <div>
              <h2>2. Ask your documentation</h2>
              <p className="muted">
                Example: “How does authentication work?”
              </p>
            </div>

            <label className="topk">
              Top-K
              <select value={topK} onChange={(e) => setTopK(Number(e.target.value))}>
                <option value={3}>3</option>
                <option value={5}>5</option>
                <option value={7}>7</option>
                <option value={10}>10</option>
              </select>
            </label>
          </div>

          <form onSubmit={askQuestion} className="question-form">
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question about your documents..."
            />
            <button className="primary" disabled={loading}>
              {loading ? "Searching..." : "Ask"}
            </button>
          </form>

          {!answer && (
            <div className="empty-state">
              <div className="big-icon">⌕</div>
              <h3>Your answer will appear here</h3>
              <p>
                The backend will embed your question, search the vector index,
                and return the most relevant documentation chunks.
              </p>
            </div>
          )}

          {answer && (
            <div className="result">
              <div className={`confidence ${answer.grounded ? "good" : "warning"}`}>
                <span>
                  {answer.grounded ? "✓ Grounded answer" : "⚠ Low evidence"}
                </span>
                <strong>
                  {(answer.confidence * 100).toFixed(1)}% similarity
                </strong>
              </div>

              <h3>Answer</h3>
              <div className="answer">{answer.answer}</div>

              <p className="note">{answer.note}</p>

              <h3>Retrieved evidence</h3>
              <div className="sources">
                {answer.sources.map((source) => (
                  <article className="source" key={`${source.filename}-${source.chunk_id}`}>
                    <div className="source-top">
                      <strong>{source.filename}</strong>
                      <span>
                        {source.page ? `Page ${source.page} · ` : ""}
                        {(source.similarity * 100).toFixed(1)}%
                      </span>
                    </div>

                    <div className="bar">
                      <div style={{ width: `${source.similarity * 100}%` }} />
                    </div>

                    <p>{source.text}</p>
                  </article>
                ))}
              </div>
            </div>
          )}
        </section>
      </main>

      <footer>
        Built as a simple college-level RAG project · FastAPI + Sentence Transformers + FAISS + React
      </footer>
    </div>
  );
}

export default App;
