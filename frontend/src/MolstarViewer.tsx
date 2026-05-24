import React, { useRef, useEffect } from 'react';

interface MolstarViewerProps {
  url: string;
  highlights?: any;
}

const MolstarViewer: React.FC<MolstarViewerProps> = ({ url, highlights }) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // Podstawowy URL - nie przekazujemy już highlights w URL, aby uniknąć błędu 414
  const viewerUrl = `/viewer.html?url=${encodeURIComponent(url)}`;

  const sendHighlights = () => {
    if (iframeRef.current && iframeRef.current.contentWindow && highlights) {
      iframeRef.current.contentWindow.postMessage({
        type: 'SET_HIGHLIGHTS',
        highlights: highlights
      }, window.location.origin);
    }
  };

  const handleIframeLoad = () => {
    sendHighlights();
  };

  // Jeśli highlights się zmienią po załadowaniu iframe, też wysyłamy wiadomość
  useEffect(() => {
    sendHighlights();
  }, [highlights]);

  return (
    <div style={{ width: '100%', height: '450px', background: '#fff', borderRadius: '8px', overflow: 'hidden', border: '1px solid #ddd' }}>
      <iframe
        ref={iframeRef}
        src={viewerUrl}
        onLoad={handleIframeLoad}
        style={{ width: '100%', height: '100%', border: 'none' }}
        title="Molstar 3D Viewer"
        allow="fullscreen"
      />
    </div>
  );
};

export default MolstarViewer;
