import { useState, useEffect, useCallback } from 'react';
import { ArrowLeft, ArrowRight, RotateCcw, Plus, ChevronLeft } from 'lucide-react';
import Button from '../../../components/ui/Button';
import IconButton from '../../../components/ui/IconButton';
import { useFlashcards } from '../../../contexts/FlashcardContext';
import FlashcardForm from '../FlashcardForm/FlashcardForm';
import './FlashcardViewer.css';

function FlashcardViewer({ deckId, onBack }) {
  const { getCardsForDeck, getCardCount, touchDeckStudied, decks } = useFlashcards();
  const cards = getCardsForDeck(deckId);
  const cardCount = getCardCount(deckId);
  const deck = decks.find(d => d.id === deckId);

  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);

  // Mark deck as studied on mount
  useEffect(() => {
    touchDeckStudied(deckId);
  }, [deckId, touchDeckStudied]);

  // Clamp index if cards get deleted (derived, not effect-based)
  const safeIndex = cards.length > 0
    ? Math.min(currentIndex, cards.length - 1)
    : 0;

  const goNext = useCallback(() => {
    setCurrentIndex(prev => {
      const next = prev + 1;
      if (next < cards.length) {
        setIsFlipped(false);
        return next;
      }
      return prev;
    });
  }, [cards.length]);

  const goPrev = useCallback(() => {
    setCurrentIndex(prev => {
      if (prev > 0) {
        setIsFlipped(false);
        return prev - 1;
      }
      return prev;
    });
  }, []);

  const flip = useCallback(() => {
    setIsFlipped(prev => !prev);
  }, []);

  // Keyboard navigation
  useEffect(() => {
    const handleKey = (e) => {
      if (showAddForm) return;
      if (e.key === 'ArrowRight') goNext();
      if (e.key === 'ArrowLeft') goPrev();
      if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); flip(); }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [goNext, goPrev, flip, showAddForm]);

  const handleCardAdded = () => {
    setShowAddForm(false);
    // Navigate to the newly added card
    setCurrentIndex(cards.length); // Will be the new last card
  };

  const progressPercent = cardCount > 0
    ? ((safeIndex + 1) / cardCount) * 100
    : 0;

  const currentCard = cards[safeIndex];

  return (
    <div className="flashcard-viewer">
      {/* Header */}
      <div className="flashcard-viewer__header">
        <button className="flashcard-viewer__back" onClick={onBack} type="button">
          <ChevronLeft size={18} />
          <span>{deck?.title || 'Back'}</span>
        </button>
        <span className="flashcard-viewer__count">
          {cardCount > 0 ? `${safeIndex + 1} / ${cardCount}` : '0 cards'}
        </span>
      </div>

      {/* Progress bar */}
      <div className="flashcard-viewer__progress">
        <div
          className="flashcard-viewer__progress-fill"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Card area */}
      {showAddForm ? (
        <FlashcardForm
          deckId={deckId}
          onDone={handleCardAdded}
          onCancel={() => setShowAddForm(false)}
        />
      ) : cardCount === 0 ? (
        <div className="flashcard-viewer__empty">
          <p>No cards in this deck yet.</p>
          <Button
            variant="primary"
            size="sm"
            leftIcon={<Plus size={16} />}
            onClick={() => setShowAddForm(true)}
          >
            Add First Card
          </Button>
        </div>
      ) : (
        <>
          {/* 3D Flip Card */}
          <div className="flashcard-viewer__scene" onClick={flip} role="button" tabIndex={0}>
            <div className={`flashcard-viewer__card ${isFlipped ? 'flashcard-viewer__card--flipped' : ''}`}>
              <div className="flashcard-viewer__face flashcard-viewer__face--front">
                <span className="flashcard-viewer__face-label">Front</span>
                <p className="flashcard-viewer__face-text">{currentCard?.front}</p>
              </div>
              <div className="flashcard-viewer__face flashcard-viewer__face--back">
                <span className="flashcard-viewer__face-label">Back</span>
                <p className="flashcard-viewer__face-text">{currentCard?.back}</p>
              </div>
            </div>
          </div>

          <p className="flashcard-viewer__hint">
            Click card or press Space to flip
          </p>

          {/* Navigation */}
          <div className="flashcard-viewer__nav">
            <IconButton
              variant="secondary"
              size="md"
              label="Previous card"
              onClick={goPrev}
              disabled={safeIndex === 0}
            >
              <ArrowLeft size={18} />
            </IconButton>

            <IconButton
              variant="ghost"
              size="md"
              label="Reset to front"
              onClick={() => setIsFlipped(false)}
            >
              <RotateCcw size={18} />
            </IconButton>

            <IconButton
              variant="secondary"
              size="md"
              label="Next card"
              onClick={goNext}
              disabled={safeIndex >= cardCount - 1}
            >
              <ArrowRight size={18} />
            </IconButton>
          </div>

          {/* Add card button */}
          <div className="flashcard-viewer__add">
            <Button
              variant="ghost"
              size="sm"
              leftIcon={<Plus size={14} />}
              onClick={() => setShowAddForm(true)}
            >
              Add Card
            </Button>
          </div>
        </>
      )}
    </div>
  );
}

export default FlashcardViewer;
