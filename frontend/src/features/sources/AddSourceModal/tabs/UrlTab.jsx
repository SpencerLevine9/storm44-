import { useState } from 'react';
import Button from '../../../../components/ui/Button';
import Input from '../../../../components/ui/Input';
import { useAddSourceModal } from '../AddSourceContext';

export default function UrlTab() {
    const { urlValue, setUrlValue, closeModal } = useAddSourceModal();
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
        // Simulate API call
        setTimeout(() => {
            setIsSubmitting(false);
            // Trigger success logic (e.g. toast, refresh sources)
            // For now we just close or show success.
            // Ideally we should call a method passed from SourcesPanel or global store to add the source.
            // We'll assume the context might handle it or we just close for now in this demo.
            console.log("Added URL:", urlValue);
            setUrlValue(''); // clear
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
