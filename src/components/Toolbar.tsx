import React from 'react';

export interface ToolbarProps {
  importHkg: boolean;
  onToggleImport: (val: boolean) => void;
}

export const Toolbar: React.FC<ToolbarProps> = ({ importHkg, onToggleImport }) => {
  return (
    <div className="toolbar">
      <label>
        <input
          type="checkbox"
          checked={importHkg}
          onChange={e => onToggleImport(e.target.checked)}
        />
        Import to hKG
      </label>
    </div>
  );
};
