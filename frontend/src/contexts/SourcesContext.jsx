import { createContext, useContext, useState, useCallback } from 'react';

const SourcesContext = createContext(null);

let nextSourceId = 1;

function generateSourceId() {
  return `src-${Date.now()}-${nextSourceId++}`;
}

export function SourcesProvider({ children }) {
  const [sources, setSources] = useState([]);

  const addSource = useCallback((notebookId, { title, type, content = null, url = null, fileName = null }) => {
    const newSource = {
      id: generateSourceId(),
      notebookId,
      title,
      type,
      status: 'ready',
      content,
      url,
      fileName,
      createdAt: new Date().toISOString(),
    };
    setSources(prev => [...prev, newSource]);
    return newSource;
  }, []);

  const removeSource = useCallback((sourceId) => {
    setSources(prev => prev.filter(s => s.id !== sourceId));
  }, []);

  const renameSource = useCallback((sourceId, newTitle) => {
    setSources(prev =>
      prev.map(s => s.id === sourceId ? { ...s, title: newTitle.trim() } : s)
    );
  }, []);

  const getSourcesForNotebook = useCallback((notebookId) => {
    return sources.filter(s => s.notebookId === notebookId);
  }, [sources]);

  return (
    <SourcesContext.Provider value={{
      sources,
      addSource,
      removeSource,
      renameSource,
      getSourcesForNotebook,
    }}>
      {children}
    </SourcesContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useSourcesContext() {
  const context = useContext(SourcesContext);
  if (!context) {
    throw new Error('useSourcesContext must be used within SourcesProvider');
  }
  return context;
}

export default SourcesContext;
