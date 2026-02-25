import { useState } from 'react';
import Button from '../../../components/ui/Button';
import { useFlashcards } from '../../../contexts/FlashcardContext';
import './FlashcardForm.css';

function FlashcardForm({ deckId, onDone, onCancel }) {
  const { addCard } = useFlashcards();
  const [front, setFront] = useState('');
  const [back, setBack] = useState('');

  const canSubmit = front.trim() && back.trim();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!canSubmit) return;
    addCard(deckId, front.trim(), back.trim());
    setFront('');
    setBack('');
    onDone?.();
  };

  const handleAddAnother = () => {
    if (!canSubmit) return;
    addCard(deckId, front.trim(), back.trim());
    setFront('');
    setBack('');
  };

  return (
    <form className="flashcard-form" onSubmit={handleSubmit}>
      <h4 className="flashcard-form__title">Add Flashcard</h4>

      <div className="flashcard-form__field">
        <label className="flashcard-form__label" htmlFor="card-front">Front</label>
        <textarea
          id="card-front"
          className="flashcard-form__textarea"
          placeholder="Question or term..."
          value={front}
          onChange={e => setFront(e.target.value)}
          rows={3}
          autoFocus
        />
      </div>

      <div className="flashcard-form__field">
        <label className="flashcard-form__label" htmlFor="card-back">Back</label>
        <textarea
          id="card-back"
          className="flashcard-form__textarea"
          placeholder="Answer or definition..."
          value={back}
          onChange={e => setBack(e.target.value)}
          rows={3}
        />
      </div>

      <div className="flashcard-form__actions">
        <Button variant="ghost" size="sm" type="button" onClick={onCancel}>
          Cancel
        </Button>
        <Button variant="secondary" size="sm" type="button" onClick={handleAddAnother} disabled={!canSubmit}>
          Add & Another
        </Button>
        <Button variant="primary" size="sm" type="submit" disabled={!canSubmit}>
          Add Card
        </Button>
      </div>
    </form>
  );
}

export default FlashcardForm;
