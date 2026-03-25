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

    const isYouTubeUrl = (url) => /youtube\.com\/watch|youtu\.be\//.test(url);

    const fetchYouTubeTitle = async (url) => {
        try {
            const res = await fetch(`/api/youtube-title?url=${encodeURIComponent(url)}`);
            if (!res.ok) return null;
            const data = await res.json();
            return data.title || null;
        } catch {
            return null;
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!isValidUrl(urlValue)) {
            setError('Please enter a valid URL');
            return;
        }

        setIsSubmitting(true);

        let title = new URL(urlValue).hostname;

        if (isYouTubeUrl(urlValue)) {
            const ytTitle = await fetchYouTubeTitle(urlValue);
            if (ytTitle) title = ytTitle;
        }

        addSource(activeNotebookId, {
            title,
            type: 'url',
            url: urlValue,
        });
        setUrlValue('');
        setIsSubmitting(false);
        closeModal();
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
