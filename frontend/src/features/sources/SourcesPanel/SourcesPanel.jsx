import { useState, useRef, useEffect } from 'react';
import {
  Plus,
  FileText,
  Search,
  MoreVertical,
  File,
  Globe,
  StickyNote,
  Check,
  X,
} from 'lucide-react';
import Button from '../../../components/ui/Button';
import IconButton from '../../../components/ui/IconButton';
import Input from '../../../components/ui/Input';
import {
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
  DropdownSeparator,
} from '../../../components/ui/Dropdown';
import { useSourcesContext } from '../../../contexts/SourcesContext';
import { useNotebooks } from '../../../contexts/NotebookContext';
import { AddSourceProvider, useAddSourceModal } from '../AddSourceModal/AddSourceContext';
import AddSourceModal from '../AddSourceModal/AddSourceModal';
import './SourcesPanel.css';

/**
 * Sources panel content - separated to use context
 */
function SourcesPanelContent() {
  const { openModal } = useAddSourceModal();
  const { getSourcesForNotebook, removeSource, renameSource } = useSourcesContext();
  const { activeNotebookId } = useNotebooks();
  const sources = getSourcesForNotebook(activeNotebookId);

  const [searchQuery, setSearchQuery] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editValue, setEditValue] = useState('');
  const editRef = useRef(null);

  useEffect(() => {
    if (editingId && editRef.current) {
      editRef.current.focus();
      editRef.current.select();
    }
  }, [editingId]);

  const startRename = (source) => {
    setEditingId(source.id);
    setEditValue(source.title);
  };

  const confirmRename = () => {
    if (editValue.trim() && editingId) {
      renameSource(editingId, editValue);
    }
    setEditingId(null);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') confirmRename();
    if (e.key === 'Escape') setEditingId(null);
  };

  const filteredSources = sources.filter(source =>
    source.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getSourceIcon = (type) => {
    switch (type) {
      case 'pdf':
        return <File size={16} />;
      case 'url':
        return <Globe size={16} />;
      case 'note':
        return <StickyNote size={16} />;
      default:
        return <FileText size={16} />;
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'ready':
        return 'source-item__status--ready';
      case 'processing':
        return 'source-item__status--processing';
      case 'error':
        return 'source-item__status--error';
      default:
        return '';
    }
  };

  return (
    <div className="sources-panel">
      {/* Header */}
      <div className="panel-header">
        <h2 className="panel-header__title">Sources</h2>
        <div className="panel-header__actions">
          <IconButton
            variant="ghost"
            size="sm"
            label="Add source"
            onClick={() => openModal('upload')}
          >
            <Plus size={18} />
          </IconButton>
        </div>
      </div>

      {/* Search */}
      <div className="sources-panel__search">
        <Input
          type="search"
          placeholder="Search sources..."
          size="sm"
          fullWidth
          leftIcon={<Search size={16} />}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Source list */}
      <div className="sources-panel__list panel-scrollable">
        {filteredSources.length > 0 ? (
          filteredSources.map(source => (
            <div key={source.id} className="source-item">
              <span className="source-item__icon">
                {getSourceIcon(source.type)}
              </span>
              <div className="source-item__content">
                {editingId === source.id ? (
                  <div className="source-item__edit">
                    <input
                      ref={editRef}
                      className="source-item__edit-input"
                      value={editValue}
                      onChange={e => setEditValue(e.target.value)}
                      onKeyDown={handleKeyDown}
                      onBlur={confirmRename}
                    />
                    <button className="source-item__edit-btn" onClick={confirmRename} type="button" aria-label="Confirm">
                      <Check size={12} />
                    </button>
                    <button className="source-item__edit-btn" onMouseDown={e => { e.preventDefault(); setEditingId(null); }} type="button" aria-label="Cancel">
                      <X size={12} />
                    </button>
                  </div>
                ) : (
                  <>
                    <span className="source-item__title">{source.title}</span>
                    <span className={`source-item__status ${getStatusClass(source.status)}`}>
                      {source.status}
                    </span>
                  </>
                )}
              </div>
              <Dropdown>
                <DropdownTrigger>
                  <IconButton variant="ghost" size="sm" label="More options">
                    <MoreVertical size={16} />
                  </IconButton>
                </DropdownTrigger>
                <DropdownMenu align="end">
                  <DropdownItem>Preview</DropdownItem>
                  <DropdownItem onClick={() => startRename(source)}>Rename</DropdownItem>
                  <DropdownSeparator />
                  <DropdownItem destructive onClick={() => removeSource(source.id)}>Delete</DropdownItem>
                </DropdownMenu>
              </Dropdown>
            </div>
          ))
        ) : (
          <div className="sources-panel__empty">
            <FileText size={40} className="sources-panel__empty-icon" />
            <p className="sources-panel__empty-title">No sources yet</p>
            <p className="sources-panel__empty-text">
              Add PDFs, URLs, or notes to get started
            </p>
            <Button
              variant="primary"
              size="sm"
              leftIcon={<Plus size={16} />}
              onClick={() => openModal('upload')}
            >
              Add Source
            </Button>
          </div>
        )}
      </div>

      {/* Modal */}
      <AddSourceModal />
    </div>
  );
}

/**
 * Wrapper to provide context
 */
function SourcesPanel() {
  return (
    <AddSourceProvider>
      <SourcesPanelContent />
    </AddSourceProvider>
  );
}

export default SourcesPanel;
