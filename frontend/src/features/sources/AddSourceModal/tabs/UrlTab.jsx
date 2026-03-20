import { useState } from 'react';
import Button from '../../../../components/ui/Button';
import Input from '../../../../components/ui/Input';
import { useAddSourceModal } from '../AddSourceContext';
import { useSourcesContext } from '../../../../contexts/SourcesContext';
import { useNotebooks } from '../../../../contexts/NotebookContext';

export default function UrlTab() {
    const { urlValue, setUrlValue, closeModal } = useAddSourceModal();
    const { addSource } = useSourcesContext();
    const { activeNotebookId } = useNotebooks();
    const [error, setError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const isValidUrl = (string) => {
        try {
            new URL(string);
            return true;
        } catch {
            return false;
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setError('');

        if (!isValidUrl(urlValue)) {
            setError('Please enter a valid URL');
            return;
        }

        setIsSubmitting(true);
        setTimeout(() => {
            setIsSubmitting(false);
            const hostname = new URL(urlValue).hostname;
            addSource(activeNotebookId, {
                title: hostname,
                type: 'url',
                url: urlValue,
            });
            setUrlValue('');
            closeModal();
        }, 1000);
    };

    return (
        <form onSubmit={handleSubmit} className="add-source-tab">
            <Input
                label="Page URL"
                placeholder="https://example.com/article"
                value={urlValue}
                onChange={(e) => {
                    setUrlValue(e.target.value);
                    if (error) setError('');
                }}
                error={error}
                autoFocus
            />

            <div className="modal__footer-actions">
                <Button
                    type="submit"
                    variant="primary"
                    isLoading={isSubmitting}
                    disabled={!urlValue}
                >
                    Add URL
                </Button>
            </div>
        </form>
    );
}
