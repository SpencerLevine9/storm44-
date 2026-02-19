import { useState, useRef, useEffect } from 'react';
import { ChevronDown, Plus, Pencil, Trash2, Check, X } from 'lucide-react';
import {
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
} from '../../ui/Dropdown';
import { useNotebooks } from '../../../contexts/NotebookContext';
import './NotebookDropdown.css';

function NotebookDropdown() {
  const {
    notebooks,
    activeNotebook,
    createNotebook,
    renameNotebook,
    deleteNotebook,
    switchNotebook,
  } = useNotebooks();

  const [editingId, setEditingId] = useState(null);
  const [editValue, setEditValue] = useState('');
  const editInputRef = useRef(null);

  useEffect(() => {
    if (editingId && editInputRef.current) {
      editInputRef.current.focus();
      editInputRef.current.select();
    }
  }, [editingId]);

  const startRename = (e, notebook) => {
    e.stopPropagation();
    setEditingId(notebook.id);
    setEditValue(notebook.name);
  };

  const confirmRename = () => {
    if (editValue.trim() && editingId) {
      renameNotebook(editingId, editValue);
    }
    setEditingId(null);
    setEditValue('');
  };

  const cancelRename = () => {
    setEditingId(null);
    setEditValue('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      confirmRename();
    } else if (e.key === 'Escape') {
      cancelRename();
    }
  };

  const handleDelete = (e, id) => {
    e.stopPropagation();
    deleteNotebook(id);
  };

  const handleCreate = (e) => {
    e.stopPropagation();
    createNotebook();
  };

  return (
    <Dropdown className="notebook-dropdown">
      <DropdownTrigger>
        <button className="notebook-dropdown__trigger" type="button">
          <span className="notebook-dropdown__name">
            {activeNotebook?.name || 'Select Notebook'}
          </span>
          <ChevronDown size={14} className="notebook-dropdown__chevron" />
        </button>
      </DropdownTrigger>
      <DropdownMenu className="notebook-dropdown__menu">
        <div className="notebook-dropdown__label">Notebooks</div>
        <div className="notebook-dropdown__list">
          {notebooks.map(notebook => (
            <div
              key={notebook.id}
              className={`notebook-dropdown__item ${notebook.id === activeNotebook?.id ? 'notebook-dropdown__item--active' : ''}`}
              onClick={() => { if (!editingId) switchNotebook(notebook.id); }}
              role="menuitem"
              tabIndex={0}
            >
              {editingId === notebook.id ? (
                <div className="notebook-dropdown__edit" onClick={e => e.stopPropagation()}>
                  <input
                    ref={editInputRef}
                    className="notebook-dropdown__edit-input"
                    value={editValue}
                    onChange={e => setEditValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    onBlur={confirmRename}
                  />
                  <button
                    className="notebook-dropdown__edit-btn"
                    onClick={confirmRename}
                    type="button"
                    aria-label="Confirm rename"
                  >
                    <Check size={14} />
                  </button>
                  <button
                    className="notebook-dropdown__edit-btn"
                    onMouseDown={e => { e.preventDefault(); cancelRename(); }}
                    type="button"
                    aria-label="Cancel rename"
                  >
                    <X size={14} />
                  </button>
                </div>
              ) : (
                <>
                  <span className="notebook-dropdown__item-name">{notebook.name}</span>
                  <div className="notebook-dropdown__item-actions">
                    <button
                      className="notebook-dropdown__action-btn"
                      onClick={e => startRename(e, notebook)}
                      type="button"
                      aria-label="Rename notebook"
                    >
                      <Pencil size={12} />
                    </button>
                    {notebooks.length > 1 && (
                      <button
                        className="notebook-dropdown__action-btn notebook-dropdown__action-btn--danger"
                        onClick={e => handleDelete(e, notebook.id)}
                        type="button"
                        aria-label="Delete notebook"
                      >
                        <Trash2 size={12} />
                      </button>
                    )}
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
        <div className="notebook-dropdown__footer">
          <button
            className="notebook-dropdown__create-btn"
            onClick={handleCreate}
            type="button"
          >
            <Plus size={14} />
            <span>New Notebook</span>
          </button>
        </div>
      </DropdownMenu>
    </Dropdown>
  );
}

export default NotebookDropdown;
