import { createContext, useContext, useState, useCallback } from 'react';
import { chatCompletion } from '../utils/openai';

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
  const generateAIDeck = useCallback(async (notebookId, title, prompt, count) => {
    const systemPrompt =
      'You are a flashcard generator. You must respond with valid JSON only. ' +
      'Return an object with a "cards" array. Each card has "front" (question) and "back" (answer) strings. ' +
      `Generate exactly ${count} flashcards.`;

    const userPrompt =
      `Topic/Material: ${prompt}\n\n` +
      `Create ${count} flashcards. ` +
      'Keep questions clear and answers concise.';

    const raw = await chatCompletion(systemPrompt, userPrompt, {
      maxTokens: count * 100,
      temperature: 0.7,
      json: true,
    });

    const parsed = JSON.parse(raw);
    const flashcards = parsed.cards || parsed.flashcards || [];

    const deck = createDeck(notebookId, title, { isAiGenerated: true });

    const newCards = flashcards.slice(0, count).map((card, i) => ({
      id: generateCardId(),
      deckId: deck.id,
      front: card.front || '',
      back: card.back || '',
      position: i,
      createdAt: new Date().toISOString(),
    }));

    setCards(prev => [...prev, ...newCards]);
    return deck;
  }, [createDeck]);

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
      generateAIDeck,
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
