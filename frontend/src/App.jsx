import React, { useState, useEffect } from 'react';
import { FileText, MessageSquare, Github } from 'lucide-react';
import axios from 'axios';
import FileUpload from './components/FileUpload';
import ChatInterface from './components/ChatInterface';
import ErrorMessage from './components/ErrorMessage';

function App() {
  const [backendStatus, setBackendStatus] = useState('checking');
  const [error, setError] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  useEffect(() => {
    checkBackend();
  }, []);

  const checkBackend = async () => {
    try {
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/`);
      if (response.data.status === 'active') {
        setBackendStatus('connected');
        if (!response.data.llm_ready) {
          setError('OpenAI API Key is missing in backend. Chat functionality will be limited.');
        }
      }
    } catch (err) {
      setBackendStatus('disconnected');
      setError('Cannot connect to backend server. Please ensure it is running.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 text-gray-900 font-sans selection:bg-primary/20">
      <ErrorMessage message={error} />

      {/* Navbar */}
      <nav className="sticky top-0 z-40 w-full backdrop-blur-lg bg-white/70 border-b border-gray-200/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="bg-primary/10 p-2 rounded-lg">
                <FileText className="w-6 h-6 text-primary" />
              </div>
              <span className="font-bold text-xl tracking-tight text-gray-900">DocuChat AI</span>
            </div>
            <div className="flex items-center gap-4">
              <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${backendStatus === 'connected'
                ? 'bg-green-100 text-green-700'
                : 'bg-red-100 text-red-700'
                }`}>
                <span className={`w-2 h-2 rounded-full ${backendStatus === 'connected' ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                {backendStatus === 'connected' ? 'System Online' : 'System Offline'}
              </div>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">

          {/* Left Column: Introduction & Upload */}
          <div className="lg:col-span-5 space-y-8">
            <div className="space-y-4">
              <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl mb-4">
                Chat with your <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-600">Documents</span>
              </h1>
              <p className="text-lg text-gray-600 leading-relaxed">
                Upload your PDF or TXT files and instantly start asking questions.
                Our AI analyzes your content to provide accurate, context-aware answers.
              </p>
            </div>

            <div className="glass-panel p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <UploadIcon className="w-5 h-5 text-primary" />
                Upload Documents
              </h3>
              <FileUpload onUploadComplete={(files) => setUploadedFiles(files)} />
            </div>

            {uploadedFiles.length > 0 && (
              <div className="bg-white/50 rounded-2xl p-6 border border-gray-100">
                <h3 className="font-semibold text-gray-900 mb-3">Uploaded Documents</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm text-left">
                    <thead className="text-xs text-gray-500 uppercase bg-gray-50/50">
                      <tr>
                        <th className="px-3 py-2">File Name</th>
                        <th className="px-3 py-2">Chunks</th>
                        <th className="px-3 py-2">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {uploadedFiles.map((file, idx) => (
                        <tr key={idx} className="hover:bg-gray-50/50">
                          <td className="px-3 py-2 font-medium text-gray-900">{file.name}</td>
                          <td className="px-3 py-2 text-gray-500">{file.chunks}</td>
                          <td className="px-3 py-2">
                            <a
                              href={file.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-primary hover:text-primary/80 hover:underline"
                            >
                              Open File
                            </a>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            <div className="bg-white/50 rounded-2xl p-6 border border-gray-100">
              <h3 className="font-semibold text-gray-900 mb-3">Features</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center gap-2">
                  <CheckIcon className="w-4 h-4 text-green-500" />
                  Instant PDF & Text analysis
                </li>
                <li className="flex items-center gap-2">
                  <CheckIcon className="w-4 h-4 text-green-500" />
                  Context-aware AI responses
                </li>
                <li className="flex items-center gap-2">
                  <CheckIcon className="w-4 h-4 text-green-500" />
                  Secure local processing
                </li>
              </ul>
            </div>
          </div>

          {/* Right Column: Chat Interface */}
          <div className="lg:col-span-7">
            <ChatInterface />
          </div>
        </div>
      </main>
    </div>
  );
}

// Small helper icons
const UploadIcon = ({ className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" x2="12" y1="3" y2="15" /></svg>
);

const CheckIcon = ({ className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><polyline points="20 6 9 17 4 12" /></svg>
);

export default App;
