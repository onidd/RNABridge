import React from 'react';

interface MolstarViewerProps {
  url: string; 
  highlights?: any;
}

const MolstarViewer: React.FC<MolstarViewerProps> = ({ url, highlights }) => {
  // Podstawowy URL z opcjonalnym podświetlaniem
  let viewerUrl = `/viewer.html?url=${encodeURIComponent(url)}`;
  
  if (highlights) {
    viewerUrl += `&highlights=${encodeURIComponent(JSON.stringify(highlights))}`;
  }

  return (
    <div style={{ width: '100%', height: '450px', background: '#fff', borderRadius: '8px', overflow: 'hidden', border: '1px solid #ddd' }}>
      <iframe 
        src={viewerUrl} 
        style={{ width: '100%', height: '100%', border: 'none' }}
        title="Molstar 3D Viewer"
        allow="fullscreen"
      />
    </div>
  );
};

export default MolstarViewer;
