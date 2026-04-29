import { createContext, useContext, useState, useCallback } from 'react';

const BACKEND_API_URL = import.meta.env.VITE_BACKEND_API_URL || 'http://127.0.0.1:8000';
const FlashcardContext = createContext(null);

let nextDeckId = 1;
let nextCardId = 1;

function generateDeckId() {
  return `deck-${Date.now()}-${nextDeckId++}`;
}
function generateCardId() {
  return `card-${Date.now()}-${nextCardId++}`;
}

export function FlashcardProvider({ children }) {
  const [decks, setDecks] = useState([]);
  const [cards, setCards] = useState([]);

  // --- Deck CRUD ---
  const createDeck = useCallback((notebookId, title = 'Untitled Deck', { isAiGenerated = false } = {}) => {
    const newDeck = {
      id: generateDeckId(),
      notebookId,
      title,
      createdAt: new Date().toISOString(),
      lastStudiedAt: null,
      isAiGenerated,
    };
    setDecks(prev => [...prev, newDeck]);
    return newDeck;
  }, []);

  const renameDeck = useCallback((deckId, newTitle) => {
    setDecks(prev =>
      prev.map(d => d.id === deckId ? { ...d, title: newTitle.trim() } : d)
    );
  }, []);

  const deleteDeck = useCallback((deckId) => {
    setDecks(prev => prev.filter(d => d.id !== deckId));
    setCards(prev => prev.filter(c => c.deckId !== deckId));
  }, []);

  const getDecksForNotebook = useCallback((notebookId) => {
    return decks.filter(d => d.notebookId === notebookId);
  }, [decks]);

  const touchDeckStudied = useCallback((deckId) => {
    setDecks(prev =>
      prev.map(d =>
        d.id === deckId ? { ...d, lastStudiedAt: new Date().toISOString() } : d
      )
    );
  }, []);

  // --- Card CRUD ---
  const addCard = useCallback((deckId, front, back) => {
    const deckCards = cards.filter(c => c.deckId === deckId);
    const newCard = {
      id: generateCardId(),
      deckId,
      front,
      back,
      position: deckCards.length,
      createdAt: new Date().toISOString(),
    };
    setCards(prev => [...prev, newCard]);
    return newCard;
  }, [cards]);

  const updateCard = useCallback((cardId, front, back) => {
    setCards(prev =>
      prev.map(c => c.id === cardId ? { ...c, front, back } : c)
    );
  }, []);

  const deleteCard = useCallback((cardId) => {
    setCards(prev => prev.filter(c => c.id !== cardId));
  }, []);

  const getCardsForDeck = useCallback((deckId) => {
    return cards
      .filter(c => c.deckId === deckId)
      .sort((a, b) => a.position - b.position);
  }, [cards]);

  const getCardCount = useCallback((deckId) => {
    return cards.filter(c => c.deckId === deckId).length;
  }, [cards]);

  // --- AI Deck Generation ---
  const generateAIDeck = useCallback(async (notebookId, title, prompt, count, { sources = [], onStatus } = {}) => {
    onStatus?.('Generating flashcards...');

    const sourceIds = sources.map((source) => source.id).filter(Boolean);

    const response = await fetch(`${BACKEND_API_URL}/api/v1/flashcards`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        topic: prompt,
        source_ids: sourceIds,
        count,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const msg = errorData?.detail
        ? JSON.stringify(errorData.detail)
        : errorData?.message;

      throw new Error(msg || `Backend error: ${response.status}`);
    }

    const data = await response.json();
    const flashcards = data?.cards || [];

    const deck = createDeck(notebookId, title, { isAiGenerated: true });

    const newCards = flashcards.slice(0, count).map((card, i) => ({
      id: generateCardId(),
      deckId: deck.id,
      front: card.front || '',
      back: card.back || '',
      position: i,
      createdAt: new Date().toISOString(),
    }));

    setCards((prev) => [...prev, ...newCards]);
    return deck;
  }, [createDeck]);

  return (
    <FlashcardContext.Provider
      value={{
        decks,
        cards,
        createDeck,
        renameDeck,
        deleteDeck,
        getDecksForNotebook,
        touchDeckStudied,
        addCard,
        updateCard,
        deleteCard,
        getCardsForDeck,
        getCardCount,
        generateAIDeck,
      }}
    >
      {children}
    </FlashcardContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useFlashcards() {
  const context = useContext(FlashcardContext);
  if (!context) {
    throw new Error('useFlashcards must be used within FlashcardProvider');
  }
  return context;
}

export default FlashcardContext;