import { useState } from 'react';
import { BookOpen, HelpCircle, Gamepad2, Plus, Sparkles, Maximize2, Minimize2 } from 'lucide-react';
import { Tabs, TabList, Tab, TabPanel } from '../../../components/ui/Tabs';
import Button from '../../../components/ui/Button';
import IconButton from '../../../components/ui/IconButton';
import { useLayout } from '../../../components/layout/WorkspaceLayout/LayoutContext';
import './StudyToolsPanel.css';

// Storage key for persisting last selected tab
const TAB_STORAGE_KEY = 'study-tools-tab';

/**
 * Study Tools panel - right sidebar with tabs for Flashcards, Quizzes, Mini-game
 */
function StudyToolsPanel() {
  const {
    studyToolsFullscreen,
    enterFullscreen,
    exitFullscreen,
    setRightPanelWidthPreset,
    isMobile
  } = useLayout();

  const [activeTab, setActiveTab] = useState(() => {
    try {
      return localStorage.getItem(TAB_STORAGE_KEY) || 'flashcards';
    } catch {
      return 'flashcards';
    }
  });

  const handleTabChange = (value) => {
    setActiveTab(value);
    try {
      localStorage.setItem(TAB_STORAGE_KEY, value);
    } catch {
      // Ignore storage errors
    }
  };

  return (
    <div className="study-tools-panel">
      {/* Header */}
      <div className="panel-header">
        <h2 className="panel-header__title">Study Tools</h2>
        <div className="panel-header__actions">
          {!isMobile && !studyToolsFullscreen && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setRightPanelWidthPreset(0.67)}
              title="Resize view to 2/3 width"
            >
              2/3 Study
            </Button>
          )}
          <IconButton
            variant="ghost"
            size="sm"
            label={studyToolsFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
            onClick={studyToolsFullscreen ? exitFullscreen : enterFullscreen}
          >
            {studyToolsFullscreen ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
          </IconButton>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={handleTabChange}>
        <div className="study-tools-panel__tabs">
          <TabList aria-label="Study tools">
            <Tab value="flashcards">
              <BookOpen size={16} />
              <span>Flashcards</span>
            </Tab>
            <Tab value="quizzes">
              <HelpCircle size={16} />
              <span>Quizzes</span>
            </Tab>
            <Tab value="game">
              <Gamepad2 size={16} />
              <span>Game</span>
            </Tab>
          </TabList>
        </div>

        {/* Flashcards Panel */}
        <TabPanel value="flashcards">
          <div className="study-tools-panel__content">
            <div className="study-tools-empty">
              <BookOpen size={48} className="study-tools-empty__icon" />
              <h3 className="study-tools-empty__title">No flashcards yet</h3>
              <p className="study-tools-empty__text">
                Generate flashcards from your selected sources to start studying.
              </p>
              <div className="study-tools-empty__actions">
                <Button
                  variant="primary"
                  size="sm"
                  leftIcon={<Sparkles size={16} />}
                >
                  Generate Flashcards
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  leftIcon={<Plus size={16} />}
                >
                  Create Manually
                </Button>
              </div>
            </div>
          </div>
        </TabPanel>

        {/* Quizzes Panel */}
        <TabPanel value="quizzes">
          <div className="study-tools-panel__content">
            <div className="study-tools-empty">
              <HelpCircle size={48} className="study-tools-empty__icon" />
              <h3 className="study-tools-empty__title">No quizzes yet</h3>
              <p className="study-tools-empty__text">
                Generate quizzes from your selected sources to test your knowledge.
              </p>
              <div className="study-tools-empty__actions">
                <Button
                  variant="primary"
                  size="sm"
                  leftIcon={<Sparkles size={16} />}
                >
                  Generate Quiz
                </Button>
              </div>
            </div>
          </div>
        </TabPanel>

        {/* Game Panel */}
        <TabPanel value="game">
          <div className="study-tools-panel__content">
            <div className="study-tools-empty">
              <Gamepad2 size={48} className="study-tools-empty__icon" />
              <h3 className="study-tools-empty__title">Match Terms</h3>
              <p className="study-tools-empty__text">
                Test your knowledge by matching terms with their definitions.
              </p>
              <div className="study-tools-empty__actions">
                <Button
                  variant="primary"
                  size="sm"
                  leftIcon={<Sparkles size={16} />}
                >
                  Start Game
                </Button>
              </div>
            </div>
          </div>
        </TabPanel>
      </Tabs>
    </div>
  );
}

export default StudyToolsPanel;
