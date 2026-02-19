import { createContext, useContext, useState, useCallback } from 'react';

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
  const createDeck = useCallback((notebookId, title = 'Untitled Deck') => {
    const newDeck = {
      id: generateDeckId(),
      notebookId,
      title,
      createdAt: new Date().toISOString(),
      lastStudiedAt: null,
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

  return (
    <FlashcardContext.Provider value={{
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
    }}>
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
