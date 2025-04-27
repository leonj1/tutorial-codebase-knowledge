import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';

function Sidebar({ docTree, isLoading }) {
  const location = useLocation();
  const [expandedFolders, setExpandedFolders] = useState({});

  const toggleFolder = (path) => {
    setExpandedFolders(prev => ({
      ...prev,
      [path]: !prev[path]
    }));
  };

  // Recursively render the document tree
  const renderTree = (items, basePath = '') => {
    if (!items || items.length === 0) return null;

    return (
      <ul className="pl-4">
        {items.map((item) => {
          // Use the item.path directly without combining with basePath
          // This avoids duplicate directory names in the path
          const itemPath = item.path;
          
          if (item.type === 'directory') {
            const isExpanded = expandedFolders[itemPath] !== false; // Default to expanded
            
            return (
              <li key={itemPath} className="mb-1">
                <div 
                  className="flex items-center cursor-pointer py-1 hover:text-blue-600 dark:hover:text-blue-400"
                  onClick={() => toggleFolder(itemPath)}
                >
                  <span className="mr-1">{isExpanded ? '▼' : '►'}</span>
                  <span className="font-medium">{item.name}</span>
                </div>
                {isExpanded && renderTree(item.children, itemPath)}
              </li>
            );
          } else if (item.type === 'file' && item.path.endsWith('.md')) {
            const displayPath = `/docs/${itemPath}`;
            const isActive = location.pathname === displayPath;
            
            return (
              <li key={itemPath} className="mb-1">
                <NavLink 
                  to={displayPath}
                  className={`nav-link ${isActive ? 'active' : ''}`}
                >
                  {item.name.replace(/\.md$/, '')}
                </NavLink>
              </li>
            );
          }
          
          return null;
        })}
      </ul>
    );
  };

  return (
    <aside className="sidebar">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h1 className="text-xl font-bold">Documentation</h1>
      </div>
      
      <nav className="p-4">
        {isLoading ? (
          <div className="flex justify-center p-4">
            <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          renderTree(docTree)
        )}
      </nav>
      
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 mt-auto">
        <button 
          className="w-full px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          onClick={() => document.documentElement.classList.toggle('dark')}
        >
          Toggle Dark Mode
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
