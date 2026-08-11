import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { UploadCloud, FileText, Trash2, RefreshCw, Filter, Search, CheckCircle2, AlertCircle } from 'lucide-react';

export default function AdminDashboard({ onLogout }) {
  const [documents, setDocuments] = useState([]);
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('Academic');
  const [fileToUpload, setFileToUpload] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isReindexing, setIsReindexing] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);

  const categories = ['Academic', 'Administrative', 'Placement', 'Admissions', 'Examination', 'General'];

  useEffect(() => {
    fetchDocuments();
  }, [categoryFilter, searchQuery]);

  const fetchDocuments = async () => {
    try {
      const data = await api.getDocuments(
        categoryFilter !== 'all' ? categoryFilter : null,
        searchQuery ? searchQuery : null
      );
      setDocuments(data.documents || []);
    } catch (err) {
      console.error("Failed to load documents", err);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFileToUpload(e.target.files[0]);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!fileToUpload) return;

    setIsUploading(true);
    setStatusMessage(null);
    try {
      const res = await api.uploadPdf(fileToUpload, selectedCategory);
      setStatusMessage({ type: 'success', text: `Uploaded & indexed '${fileToUpload.name}' into MinIO & Vector DB!` });
      setFileToUpload(null);
      fetchDocuments();
    } catch (err) {
      setStatusMessage({ type: 'error', text: err.message || 'PDF upload failed.' });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (docId, filename) => {
    if (!window.confirm(`Are you sure you want to delete '${filename}'? This will automatically remove it from MinIO object storage and Qdrant Vector DB.`)) return;

    try {
      await api.deleteDocument(docId);
      setStatusMessage({ type: 'success', text: `Document '${filename}' dynamically removed from MinIO & Vector DB.` });
      fetchDocuments();
    } catch (err) {
      setStatusMessage({ type: 'error', text: err.message || 'Failed to delete document.' });
    }
  };

  const handleReindex = async () => {
    setIsReindexing(true);
    setStatusMessage(null);
    try {
      const res = await api.reindexDocuments();
      setStatusMessage({ type: 'success', text: res.message });
      fetchDocuments();
    } catch (err) {
      setStatusMessage({ type: 'error', text: err.message || 'Re-indexing failed.' });
    } finally {
      setIsReindexing(false);
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem 1rem' }}>
      {/* Header Banner */}
      <div className="glass-panel" style={{ padding: '1.5rem 2rem', marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: '800', background: 'var(--primary-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Admin PDF & Vector DB Control Center
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            Upload PDFs to MinIO, store metadata in MongoDB, and automatically synchronize vector embeddings in Qdrant.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <button onClick={handleReindex} disabled={isReindexing} className="btn-secondary">
            <RefreshCw size={18} className={isReindexing ? "pulse-glow" : ""} />
            {isReindexing ? "Re-indexing Vector DB..." : "Force Vector DB Sync"}
          </button>
          <button onClick={onLogout} className="btn-secondary" style={{ color: '#ef4444', borderColor: 'rgba(239, 68, 68, 0.3)' }}>
            Logout Admin
          </button>
        </div>
      </div>

      {statusMessage && (
        <div style={{ 
          padding: '1rem 1.25rem', 
          borderRadius: 'var(--radius-md)', 
          marginBottom: '1.5rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          backgroundColor: statusMessage.type === 'success' ? 'rgba(34, 197, 94, 0.15)' : 'rgba(239, 68, 68, 0.15)',
          border: `1px solid ${statusMessage.type === 'success' ? 'rgba(34, 197, 94, 0.4)' : 'rgba(239, 68, 68, 0.4)'}`,
          color: statusMessage.type === 'success' ? '#4ade80' : '#f87171'
        }}>
          {statusMessage.type === 'success' ? <CheckCircle2 size={20} /> : <AlertCircle size={20} />}
          <span>{statusMessage.text}</span>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
        {/* PDF Upload Card */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <UploadCloud size={22} color="#3b82f6" /> Add PDF Document
          </h2>
          <form onSubmit={handleUpload}>
            <div style={{ marginBottom: '1.25rem' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                Document Category
              </label>
              <select 
                value={selectedCategory} 
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="input-field"
                style={{ cursor: 'pointer' }}
              >
                {categories.map(cat => (
                  <option key={cat} value={cat} style={{ background: '#111827', color: 'white' }}>{cat}</option>
                ))}
              </select>
            </div>

            <div style={{ 
              border: '2px dashed var(--glass-border)', 
              borderRadius: 'var(--radius-md)', 
              padding: '1.5rem', 
              textAlign: 'center', 
              marginBottom: '1.25rem',
              backgroundColor: 'rgba(255,255,255,0.02)',
              cursor: 'pointer'
            }}>
              <input 
                type="file" 
                accept=".pdf,.txt,.md" 
                onChange={handleFileChange} 
                id="file-upload" 
                style={{ display: 'none' }} 
              />
              <label htmlFor="file-upload" style={{ cursor: 'pointer', display: 'block' }}>
                <FileText size={36} color="var(--primary-accent)" style={{ margin: '0 auto 0.5rem auto' }} />
                <p style={{ fontWeight: '600', fontSize: '0.95rem' }}>
                  {fileToUpload ? fileToUpload.name : "Click to select PDF or drag file here"}
                </p>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                  Supports PDF, TXT, MD up to 25MB
                </p>
              </label>
            </div>

            <button 
              type="submit" 
              disabled={!fileToUpload || isUploading} 
              className="btn-primary" 
              style={{ width: '100%', justifyContent: 'center' }}
            >
              {isUploading ? "Storing in MinIO & Vectorizing..." : "Upload & Sync Vector DB"}
            </button>
          </form>
        </div>

        {/* Document Listing & Filtration */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
            <h2 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <FileText size={22} color="#8b5cf6" /> Managed Knowledge Files ({documents.length})
            </h2>

            {/* Filter Bar */}
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <div style={{ position: 'relative' }}>
                <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)' }} />
                <input 
                  type="text" 
                  placeholder="Search file..." 
                  value={searchQuery} 
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="input-field" 
                  style={{ paddingLeft: '2.25rem', width: '160px' }}
                />
              </div>

              <select 
                value={categoryFilter} 
                onChange={(e) => setCategoryFilter(e.target.value)} 
                className="input-field"
                style={{ width: '140px' }}
              >
                <option value="all" style={{ background: '#111827' }}>All Categories</option>
                {categories.map(cat => (
                  <option key={cat} value={cat} style={{ background: '#111827' }}>{cat}</option>
                ))}
              </select>
            </div>
          </div>

          {documents.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
              <p style={{ fontSize: '1.05rem' }}>No documents matching current filters.</p>
              <p style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>Upload a new PDF on the left panel to populate the vector store.</p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--glass-border)', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '0.75rem 0.5rem' }}>File Name</th>
                    <th style={{ padding: '0.75rem 0.5rem' }}>Category</th>
                    <th style={{ padding: '0.75rem 0.5rem' }}>Size</th>
                    <th style={{ padding: '0.75rem 0.5rem' }}>Chunks</th>
                    <th style={{ padding: '0.75rem 0.5rem' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc) => (
                    <tr key={doc.doc_id} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                      <td style={{ padding: '0.85rem 0.5rem', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <FileText size={18} color="#60a5fa" />
                        <span style={{ maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={doc.filename}>
                          {doc.filename}
                        </span>
                      </td>
                      <td style={{ padding: '0.85rem 0.5rem' }}>
                        <span className="badge badge-purple">{doc.category || 'General'}</span>
                      </td>
                      <td style={{ padding: '0.85rem 0.5rem', color: 'var(--text-muted)' }}>
                        {(doc.file_size / 1024).toFixed(1)} KB
                      </td>
                      <td style={{ padding: '0.85rem 0.5rem' }}>
                        <span className="badge badge-blue">{doc.chunk_count || 0} Chunks</span>
                      </td>
                      <td style={{ padding: '0.85rem 0.5rem' }}>
                        <button 
                          onClick={() => handleDelete(doc.doc_id, doc.filename)} 
                          style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', padding: '0.25rem' }}
                          title="Delete PDF & remove vectors"
                        >
                          <Trash2 size={18} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
