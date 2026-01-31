import { useState, useCallback } from 'react';
import { WorkspaceLayout, Header } from '../../components/layout';
import SourcesPanel from '../../features/sources/SourcesPanel';
import ChatPanel from '../../features/chat/ChatPanel';
import StudyToolsPanel from '../../features/study-tools/StudyToolsPanel';
import './WorkspacePage.css';

/**
 * Main workspace page with 3-panel layout
 */
function WorkspacePage() {
  const [workspaceName, setWorkspaceName] = useState('My Study Workspace');
  const [conversationId, setConversationId] = useState(() => Date.now().toString());

  const handleNewChat = useCallback(() => {
    // Reset conversation state
    setConversationId(Date.now().toString());
  }, []);

  const handleRename = useCallback(() => {
    const newName = prompt('Enter workspace name:', workspaceName);
    if (newName && newName.trim()) {
      setWorkspaceName(newName.trim());
    }
  }, [workspaceName]);

  return (
    <WorkspaceLayout
      header={
        <Header 
          workspaceName={workspaceName}
          onNewChat={handleNewChat}
          onRename={handleRename}
        />
      }
      leftPanel={<SourcesPanel />}
      rightPanel={<StudyToolsPanel />}
    >
      <ChatPanel key={conversationId} />
    </WorkspaceLayout>
  );
}

export default WorkspacePage;
