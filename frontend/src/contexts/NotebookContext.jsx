import { createContext, useContext, useState, useCallback } from 'react';

const NotebookContext = createContext(null);

let nextId = 1;
function generateId() {
  return `nb-${Date.now()}-${nextId++}`;
}

export function NotebookProvider({ children }) {
  const [notebooks, setNotebooks] = useState(() => {
    const defaultNotebook = {
      id: 'nb-default',
      name: 'My Study Workspace',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    return [defaultNotebook];
  });
  const [activeNotebookId, setActiveNotebookId] = useState('nb-default');

  const activeNotebook = notebooks.find(nb => nb.id === activeNotebookId) || notebooks[0];

  const createNotebook = useCallback((name = 'Untitled Notebook') => {
    const newNotebook = {
      id: generateId(),
      name,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    setNotebooks(prev => [...prev, newNotebook]);
    setActiveNotebookId(newNotebook.id);
    return newNotebook;
  }, []);

  const renameNotebook = useCallback((id, newName) => {
    setNotebooks(prev =>
      prev.map(nb =>
        nb.id === id
          ? { ...nb, name: newName.trim(), updatedAt: new Date().toISOString() }
          : nb
      )
    );
  }, []);

  const deleteNotebook = useCallback((id) => {
    setNotebooks(prev => {
      const filtered = prev.filter(nb => nb.id !== id);
      if (filtered.length === 0) {
        const fallback = {
          id: generateId(),
          name: 'Untitled Notebook',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        return [fallback];
      }
      return filtered;
    });
    setActiveNotebookId(prev => {
      if (prev === id) {
        const remaining = notebooks.filter(nb => nb.id !== id);
        return remaining.length > 0 ? remaining[0].id : prev;
      }
      return prev;
    });
  }, [notebooks]);

  const switchNotebook = useCallback((id) => {
    setActiveNotebookId(id);
  }, []);

  return (
    <NotebookContext.Provider value={{
      notebooks,
      activeNotebook,
      activeNotebookId,
      createNotebook,
      renameNotebook,
      deleteNotebook,
      switchNotebook,
    }}>
      {children}
    </NotebookContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useNotebooks() {
  const context = useContext(NotebookContext);
  if (!context) {
    throw new Error('useNotebooks must be used within NotebookProvider');
  }
  return context;
}

export default NotebookContext;
