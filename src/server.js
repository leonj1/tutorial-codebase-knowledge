import express from 'express';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 80;

// Serve static files from the React app
app.use(express.static(path.join(__dirname, '../dist')));

// Function to recursively scan directories and build a tree structure
function scanDirectory(dir, baseDir = '') {
  const result = [];
  const items = fs.readdirSync(dir);

  for (const item of items) {
    const itemPath = path.join(dir, item);
    const stat = fs.statSync(itemPath);
    const relativePath = path.relative(baseDir, itemPath);

    if (stat.isDirectory()) {
      result.push({
        type: 'directory',
        name: item,
        path: relativePath,
        children: scanDirectory(itemPath, baseDir)
      });
    } else {
      result.push({
        type: 'file',
        name: item,
        path: relativePath
      });
    }
  }

  // Sort directories first, then files, both alphabetically
  return result.sort((a, b) => {
    if (a.type === 'directory' && b.type === 'file') return -1;
    if (a.type === 'file' && b.type === 'directory') return 1;
    return a.name.localeCompare(b.name);
  });
}

// API endpoint to get the documentation structure
app.get('/docs', (req, res) => {
  try {
    const docsDir = path.join(__dirname, '../dist/docs');
    const tree = scanDirectory(docsDir, docsDir);
    res.json(tree);
  } catch (error) {
    console.error('Error scanning docs directory:', error);
    res.status(500).json({ error: 'Failed to scan documentation directory' });
  }
});

// Serve markdown files
app.get('/docs/*', (req, res) => {
  // Remove the leading '/docs/' from the path
  const relativePath = req.path.replace(/^\/docs\//, '');
  const filePath = path.join(__dirname, '../dist/docs', relativePath);
  
  console.log('Requested path:', req.path);
  console.log('Resolved file path:', filePath);
  
  // Check if the file exists
  if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
    res.sendFile(filePath);
  } else {
    // If the file doesn't exist, check if it's a directory and look for index.md
    const indexPath = path.join(filePath, 'index.md');
    if (fs.existsSync(indexPath) && fs.statSync(indexPath).isFile()) {
      res.sendFile(indexPath);
    } else {
      res.status(404).send('Document not found');
    }
  }
});

// For any other GET request, send back the React app
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../dist/index.html'));
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
