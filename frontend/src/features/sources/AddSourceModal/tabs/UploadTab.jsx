import { useCallback, useState } from 'react';
import { Upload, File, X, Check, AlertCircle } from 'lucide-react';
import Button from '../../../../components/ui/Button';
import { useAddSourceModal } from '../AddSourceContext';
import { useSourcesContext } from '../../../../contexts/SourcesContext';
import { useNotebooks } from '../../../../contexts/NotebookContext';

export default function UploadTab() {
    const { uploadQueue, setUploadQueue } = useAddSourceModal();
    const { addSource } = useSourcesContext();
    const { activeNotebookId } = useNotebooks();
    const [isDragging, setIsDragging] = useState(false);

    const uploadFile = useCallback((file) => {
        const id = Math.random().toString(36).substr(2, 9);
        setUploadQueue(prev => [...prev, { id, file, status: 'uploading', progress: 0 }]);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', file.name);

        const xhr = new XMLHttpRequest();

        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const progress = Math.round((e.loaded / e.total) * 100);
                setUploadQueue(prev => prev.map(item =>
                    item.id === id ? { ...item, progress } : item
                ));
            }
        });

        xhr.addEventListener('load', () => {
            if (xhr.status === 200) {
                const result = JSON.parse(xhr.responseText);
                setUploadQueue(prev => prev.map(item =>
                    item.id === id ? { ...item, status: 'completed', progress: 100 } : item
                ));
                addSource(activeNotebookId, {
                    id: result.source_id,
                    title: file.name,
                    type: 'pdf',
                });
            } else {
                setUploadQueue(prev => prev.map(item =>
                    item.id === id ? { ...item, status: 'error' } : item
                ));
            }
        });

        xhr.addEventListener('error', () => {
            setUploadQueue(prev => prev.map(item =>
                item.id === id ? { ...item, status: 'error' } : item
            ));
        });

        xhr.open('POST', 'http://localhost:8000/api/v1/sources/upload/pdf');
        xhr.send(formData);
    }, [setUploadQueue, addSource, activeNotebookId]);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        setIsDragging(false);

        if (e.dataTransfer.files?.length) {
            Array.from(e.dataTransfer.files).forEach(file => {
                uploadFile(file);
            });
        }
    }, [uploadFile]);

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleBrowse = () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.multiple = true;
        input.accept = '.pdf,.txt,.docx';
        input.onchange = (e) => {
            if (e.target.files?.length) {
                Array.from(e.target.files).forEach(file => {
                    uploadFile(file);
                });
            }
        };
        input.click();
    };

    return (
        <div className="add-source-tab">
            <div
                className={`dropzone ${isDragging ? 'dropzone--active' : ''}`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={handleBrowse}
            >
                <div className="dropzone__icon">
                    <Upload size={32} />
                </div>
                <div className="dropzone__text">
                    <p className="dropzone__title">Click to upload or drag and drop</p>
                    <p className="dropzone__hint">PDF, TXT (max 10MB)</p>
                </div>
            </div>

            {uploadQueue.length > 0 && (
                <div className="upload-list">
                    {uploadQueue.map(item => (
                        <div key={item.id} className="upload-item">
                            <File size={16} className="upload-item__icon" />
                            <div className="upload-item__info">
                                <span className="upload-item__name">{item.file.name}</span>
                                <div className="upload-item__bar">
                                    <div
                                        className="upload-item__progress"
                                        style={{ width: `${item.progress}%` }}
                                        data-status={item.status}
                                    />
                                </div>
                            </div>
                            <div className="upload-item__status">
                                {item.status === 'uploading' && <span className="text-xs">{item.progress}%</span>}
                                {item.status === 'completed' && <Check size={16} className="text-success" />}
                                {item.status === 'error' && <AlertCircle size={16} className="text-error" />}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
