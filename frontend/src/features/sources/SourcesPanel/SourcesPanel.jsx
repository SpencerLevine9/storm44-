import { useState } from 'react';
import {
  Plus,
  Upload,
  Link,
  FileText,
  Search,
  MoreVertical,
  File,
  Globe,
  StickyNote
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
import { SkeletonListItem } from '../../../components/ui/Skeleton';
import { AddSourceProvider, useAddSourceModal } from '../AddSourceModal/AddSourceContext';
import AddSourceModal from '../AddSourceModal/AddSourceModal';
import './SourcesPanel.css';

/**
 * Sources panel content - separated to use context
 */
function SourcesPanelContent() {
  const { openModal } = useAddSourceModal();
  const [searchQuery, setSearchQuery] = useState('');
  const [sources, setSources] = useState([
    { id: '1', title: 'Introduction to Machine Learning', type: 'pdf', status: 'ready' },
    { id: '2', title: 'Neural Networks Explained', type: 'url', status: 'ready' },
    { id: '3', title: 'My Study Notes', type: 'note', status: 'ready' },
    { id: '4', title: 'Processing document...', type: 'pdf', status: 'processing' },
  ]);
  const [selectedSources, setSelectedSources] = useState(['1', '2']);
  // const [isLoading, setIsLoading] = useState(false); 

  // Placeholder handlers for future implementation
  const handleDeleteSource = (id) => {
    setSources(prev => prev.filter(s => s.id !== id));
  };

  const filteredSources = sources.filter(source =>
    source.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleToggleSource = (id) => {
    setSelectedSources(prev =>
      prev.includes(id)
        ? prev.filter(s => s !== id)
        : [...prev, id]
    );
  };

  const handleSelectAll = () => {
    if (selectedSources.length === sources.length) {
      setSelectedSources([]);
    } else {
      setSelectedSources(sources.map(s => s.id));
    }
  };

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

      {/* Selection info */}
      <div className="sources-panel__selection">
        <button
          className="sources-panel__select-all"
          onClick={handleSelectAll}
        >
          {selectedSources.length === sources.length ? 'Deselect all' : 'Select all'}
        </button>
        <span className="sources-panel__selected-count">
          {selectedSources.length} selected
        </span>
      </div>

      {/* Source list */}
      <div className="sources-panel__list panel-scrollable">
        {filteredSources.length > 0 ? (
          filteredSources.map(source => (
            <div
              key={source.id}
              className={`source-item ${selectedSources.includes(source.id) ? 'source-item--selected' : ''}`}
            >
              <label className="source-item__checkbox">
                <input
                  type="checkbox"
                  checked={selectedSources.includes(source.id)}
                  onChange={() => handleToggleSource(source.id)}
                />
                <span className="source-item__checkmark" />
              </label>
              <span className="source-item__icon">
                {getSourceIcon(source.type)}
              </span>
              <div className="source-item__content">
                <span className="source-item__title">{source.title}</span>
                <span className={`source-item__status ${getStatusClass(source.status)}`}>
                  {source.status}
                </span>
              </div>
              <Dropdown>
                <DropdownTrigger>
                  <IconButton variant="ghost" size="sm" label="More options">
                    <MoreVertical size={16} />
                  </IconButton>
                </DropdownTrigger>
                <DropdownMenu align="end">
                  <DropdownItem>Preview</DropdownItem>
                  <DropdownItem>Rename</DropdownItem>
                  <DropdownSeparator />
                  <DropdownItem destructive onClick={() => handleDeleteSource(source.id)}>Delete</DropdownItem>
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
