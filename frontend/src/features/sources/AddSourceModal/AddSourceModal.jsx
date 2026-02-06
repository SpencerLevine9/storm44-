import { Upload, Link, FileText } from 'lucide-react';
import Modal from '../../../components/ui/Modal';
import { Tabs, TabList, Tab, TabPanel } from '../../../components/ui/Tabs';
import { useAddSourceModal } from './AddSourceContext';
import UploadTab from './tabs/UploadTab';
import UrlTab from './tabs/UrlTab';
import NoteTab from './tabs/NoteTab';
import './AddSourceModal.css';

export default function AddSourceModal() {
    const { isOpen, closeModal, activeTab, setActiveTab } = useAddSourceModal();

    return (
        <Modal
            isOpen={isOpen}
            onClose={closeModal}
            title="Add Source"
            size="lg" // 50vw approx based on existing css likely
            className="add-source-modal"
        >
            <Tabs value={activeTab} onValueChange={setActiveTab}>
                <div style={{ marginBottom: '16px' }}>
                    <TabList aria-label="Add source methods">
                        <Tab value="upload">
                            <Upload size={16} />
                            <span>Upload File</span>
                        </Tab>
                        <Tab value="url">
                            <Link size={16} />
                            <span>Add URL</span>
                        </Tab>
                        <Tab value="note">
                            <FileText size={16} />
                            <span>Create Note</span>
                        </Tab>
                    </TabList>
                </div>

                <TabPanel value="upload">
                    <UploadTab />
                </TabPanel>

                <TabPanel value="url">
                    <UrlTab />
                </TabPanel>

                <TabPanel value="note">
                    <NoteTab />
                </TabPanel>
            </Tabs>

            {/* Footer is handled within tabs or we can add a shared footer here if needed */}
        </Modal>
    );
}
