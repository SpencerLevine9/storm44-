import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import Button from '../../components/ui/Button';
import './SettingsPage.css';

/**
 * Settings page placeholder
 */
function SettingsPage() {
  const navigate = useNavigate();

  return (
    <div className="settings-page">
      <div className="settings-page__header">
        <Button
          variant="ghost"
          size="sm"
          leftIcon={<ArrowLeft size={16} />}
          onClick={() => navigate('/')}
        >
          Back to Workspace
        </Button>
        <h1 className="settings-page__title">Settings</h1>
      </div>
      
      <div className="settings-page__content">
        <div className="settings-section">
          <h2 className="settings-section__title">Appearance</h2>
          <p className="settings-section__description">
            Customize the look and feel of your workspace.
          </p>
          {/* Settings content will go here */}
          <div className="settings-placeholder">
            Settings panel coming soon...
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsPage;
