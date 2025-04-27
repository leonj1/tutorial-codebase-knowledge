import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import rehypeSlug from 'rehype-slug';
import rehypeAutolinkHeadings from 'rehype-autolink-headings';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import mermaid from 'mermaid';

// Initialize mermaid
mermaid.initialize({
  startOnLoad: true,
  theme: 'default',
  securityLevel: 'loose',
  fontFamily: 'sans-serif',
});

function MarkdownPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [content, setContent] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const isDarkMode = document.documentElement.classList.contains('dark');

  useEffect(() => {
    // Extract the path from the URL
    const path = location.pathname.replace(/^\/docs/, '');
    
    if (!path) {
      setError('No document specified');
      setIsLoading(false);
      return;
    }

    // Fetch the markdown content
    fetch(`/docs/${path.replace(/^\//, '')}`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Failed to fetch document: ${response.status}`);
        }
        return response.text();
      })
      .then(data => {
        setContent(data);
        setIsLoading(false);
        setError(null);
        
        // Process any mermaid diagrams after content is loaded
        setTimeout(() => {
          mermaid.init(undefined, document.querySelectorAll('.mermaid'));
        }, 100);
      })
      .catch(err => {
        console.error('Error fetching markdown:', err);
        setError(`Failed to load document: ${err.message}`);
        setIsLoading(false);
      });
  }, [location.pathname]);

  // Handle internal links
  const handleLinkClick = (event) => {
    const href = event.target.getAttribute('href');
    
    if (href && href.startsWith('/') && !href.startsWith('//')) {
      event.preventDefault();
      navigate(href);
    }
  };

  // Custom renderer for code blocks to handle mermaid diagrams
  const components = {
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      const language = match ? match[1] : '';
      
      if (language === 'mermaid') {
        return (
          <div className="mermaid">
            {String(children).replace(/\n$/, '')}
          </div>
        );
      }
      
      return !inline ? (
        <SyntaxHighlighter
          style={isDarkMode ? oneDark : vscDarkPlus}
          language={language}
          PreTag="div"
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      ) : (
        <code className={className} {...props}>
          {children}
        </code>
      );
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-300 px-4 py-3 rounded">
          <h2 className="text-xl font-bold mb-2">Error</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <article 
        className="markdown-content" 
        onClick={handleLinkClick}
      >
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeRaw, rehypeSlug, rehypeAutolinkHeadings]}
          components={components}
        >
          {content}
        </ReactMarkdown>
      </article>
    </div>
  );
}

export default MarkdownPage;
