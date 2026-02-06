import { useState } from 'react';
import Button from '../../../../components/ui/Button';
import TextArea from '../../../../components/ui/TextArea';
import { useAddSourceModal } from '../AddSourceContext';

export default function NoteTab() {
    const { noteValue, setNoteValue, closeModal } = useAddSourceModal();
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!noteValue.trim()) return;

        setIsSubmitting(true);
        // Simulate API call
        setTimeout(() => {
            setIsSubmitting(false);
            console.log("Added Note:", noteValue);
            setNoteValue('');
            closeModal();
        }, 1000);
    };

    return (
        <form onSubmit={handleSubmit} className="add-source-tab">
            <TextArea
                label="Note Content"
                placeholder="Type or paste your note here..."
                rows={8}
                value={noteValue}
                onChange={(e) => setNoteValue(e.target.value)}
                autoFocus
            />

            <div className="modal__footer-actions">
                <Button
                    type="submit"
                    variant="primary"
                    isLoading={isSubmitting}
                    disabled={!noteValue.trim()}
                >
                    Save Note
                </Button>
            </div>
        </form>
    );
}
