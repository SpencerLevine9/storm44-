import { useState, useRef, useEffect } from 'react';
import { Plus, Trash2, Pencil, BookOpen, Clock, Layers, Check, X } from 'lucide-react';
import Button from '../../../components/ui/Button';
import { useFlashcards } from '../../../contexts/FlashcardContext';
import { useNotebooks } from '../../../contexts/NotebookContext';
import './DeckList.css';

function DeckList({ onSelectDeck }) {
  const { activeNotebookId } = useNotebooks();
  const { getDecksForNotebook, createDeck, renameDeck, deleteDeck, getCardCount } = useFlashcards();
  const decks = getDecksForNotebook(activeNotebookId);

  const [editingId, setEditingId] = useState(null);
  const [editValue, setEditValue] = useState('');
  const editRef = useRef(null);

  useEffect(() => {
    if (editingId && editRef.current) {
      editRef.current.focus();
      editRef.current.select();
    }
  }, [editingId]);

  const handleCreate = () => {
    const deck = createDeck(activeNotebookId);
    setEditingId(deck.id);
    setEditValue(deck.title);
  };

  const startRename = (e, deck) => {
    e.stopPropagation();
    setEditingId(deck.id);
    setEditValue(deck.title);
  };

  const confirmRename = () => {
    if (editValue.trim() && editingId) {
      renameDeck(editingId, editValue);
    }
    setEditingId(null);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') confirmRename();
    if (e.key === 'Escape') setEditingId(null);
  };

  const handleDelete = (e, deckId) => {
    e.stopPropagation();
    deleteDeck(deckId);
  };

  const formatDate = (isoString) => {
    if (!isoString) return 'Never';
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  if (decks.length === 0) {
    return (
      <div className="deck-list__empty">
        <BookOpen size={48} className="deck-list__empty-icon" />
        <h3 className="deck-list__empty-title">No flashcard decks yet</h3>
        <p className="deck-list__empty-text">
          Create a deck to start adding flashcards.
        </p>
        <Button
          variant="primary"
          size="sm"
          leftIcon={<Plus size={16} />}
          onClick={handleCreate}
        >
          Create Deck
        </Button>
      </div>
    );
  }

  return (
    <div className="deck-list">
      <div className="deck-list__grid">
        {decks.map(deck => {
          const cardCount = getCardCount(deck.id);
          return (
            <div
              key={deck.id}
              className="deck-card"
              onClick={() => { if (!editingId) onSelectDeck(deck.id); }}
              role="button"
              tabIndex={0}
              onKeyDown={e => { if (e.key === 'Enter' && !editingId) onSelectDeck(deck.id); }}
            >
              <div className="deck-card__header">
                {editingId === deck.id ? (
                  <div className="deck-card__edit" onClick={e => e.stopPropagation()}>
                    <input
                      ref={editRef}
                      className="deck-card__edit-input"
                      value={editValue}
                      onChange={e => setEditValue(e.target.value)}
                      onKeyDown={handleKeyDown}
                      onBlur={confirmRename}
                    />
                    <button className="deck-card__edit-btn" onClick={confirmRename} type="button" aria-label="Confirm">
                      <Check size={12} />
                    </button>
                    <button className="deck-card__edit-btn" onMouseDown={e => { e.preventDefault(); setEditingId(null); }} type="button" aria-label="Cancel">
                      <X size={12} />
                    </button>
                  </div>
                ) : (
                  <>
                    <span className="deck-card__title">{deck.title}</span>
                    <div className="deck-card__actions">
                      <button
                        className="deck-card__action-btn"
                        onClick={e => startRename(e, deck)}
                        type="button"
                        aria-label="Rename deck"
                      >
                        <Pencil size={12} />
                      </button>
                      <button
                        className="deck-card__action-btn deck-card__action-btn--danger"
                        onClick={e => handleDelete(e, deck.id)}
                        type="button"
                        aria-label="Delete deck"
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  </>
                )}
              </div>
              <div className="deck-card__meta">
                <span className="deck-card__meta-item">
                  <Layers size={12} />
                  {cardCount} {cardCount === 1 ? 'card' : 'cards'}
                </span>
                <span className="deck-card__meta-item">
                  <Clock size={12} />
                  {formatDate(deck.lastStudiedAt)}
                </span>
              </div>
            </div>
          );
        })}
      </div>
      <div className="deck-list__footer">
        <Button
          variant="secondary"
          size="sm"
          leftIcon={<Plus size={16} />}
          onClick={handleCreate}
        >
          New Deck
        </Button>
      </div>
    </div>
  );
}

export default DeckList;
