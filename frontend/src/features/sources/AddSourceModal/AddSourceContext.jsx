import { createContext, useContext, useState, useCallback } from 'react';

const AddSourceContext = createContext(null);

// eslint-disable-next-line react-refresh/only-export-components
export function useAddSourceModal() {
    const context = useContext(AddSourceContext);
    if (!context) {
        throw new Error('useAddSourceModal must be used within AddSourceProvider');
    }
    return context;
}

export function AddSourceProvider({ children }) {
    const [isOpen, setIsOpen] = useState(false);
    const [activeTab, setActiveTab] = useState('upload'); // upload | url | note

    // Form State
    const [urlValue, setUrlValue] = useState('');
    const [noteValue, setNoteValue] = useState('');
    const [uploadQueue, setUploadQueue] = useState([]);

    // Reset state when closing
    const resetState = useCallback(() => {
        setActiveTab('upload');
        setUrlValue('');
        setNoteValue('');
        setUploadQueue([]);
    }, []);

    const openModal = useCallback((tab = 'upload') => {
        setActiveTab(tab);
        setIsOpen(true);
    }, []);

    const closeModal = useCallback(() => {
        setIsOpen(false);
        // Optional: delay reset to allow animation to finish
        setTimeout(resetState, 300);
    }, [resetState]);

    const value = {
        isOpen,
        activeTab,
        openModal,
        closeModal,
        setActiveTab,

        // Form data
        urlValue,
        setUrlValue,
        noteValue,
        setNoteValue,
        uploadQueue,
        setUploadQueue,
    };

    return (
        <AddSourceContext.Provider value={value}>
            {children}
        </AddSourceContext.Provider>
    );
}
