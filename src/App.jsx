import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import MarkdownPage from './components/MarkdownPage';

function App() {
  const [docTree, setDocTree] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const location = useLocation();

  useEffect(() => {
    // Fetch the documentation structure
    fetch('/docs')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch documentation structure');
        }
        return response.json();
      })
      .then(data => {
        setDocTree(data);
        setIsLoading(false);
      })
      .catch(error => {
        console.error('Error fetching documentation:', error);
        setIsLoading(false);
      });
  }, []);

  // Find the first document to redirect to
  const findFirstDoc = (tree) => {
    if (!tree || tree.length === 0) return null;
    
    for (const item of tree) {
      if (item.type === 'file' && item.path.endsWith('.md')) {
        return item.path;
      } else if (item.type === 'directory' && item.children) {
        const firstInChild = findFirstDoc(item.children);
        if (firstInChild) return firstInChild;
      }
    }
    
    return null;
  };

  return (
    <div className="flex min-h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <Sidebar docTree={docTree} isLoading={isLoading} />
      
      <main className="main-content flex-1">
        {isLoading ? (
          <div className="flex items-center justify-center h-screen">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <Routes>
            <Route path="/" element={<Navigate to={`/docs/${findFirstDoc(docTree)}`|| '/not-found'} replace />} />
            <Route path="/docs/*" element={<MarkdownPage />} />
            <Route path="*" element={
              <div className="flex flex-col items-center justify-center h-screen">
                <h1 className="text-4xl font-bold mb-4">404 - Not Found</h1>
                <p className="text-xl">The page you're looking for doesn't exist.</p>
              </div>
            } />
          </Routes>
        )}
      </main>
    </div>
  );
}

export default App;
