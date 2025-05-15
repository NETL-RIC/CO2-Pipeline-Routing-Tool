/**
 * Component that contains the 'Identify Route' and 'Evaluate Corridon' buttons
 */
import * as React from 'react';
import Stack from '@mui/material/Stack';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';

/**
 * The two exclusive selection buttons controlling "Pipeline Mode" and "Railway Mode" as a submode of Id Mode
 * @param {function} setBtnGroupState - Sets the tool's main mode to either Identify Route or Evaluate corridor, via "id" or "eval"
 * @param {string} btntext1 - Button string for "Identify Route"
 * @param {string} btntext2 - Button string for "Evaluate Corridor"
 * @param {funciton} setEvalModePolygon - Setter for the line/polygon drawn by Eval Mode, used here to clear it by setting to []
 * @param {funciton} setIdModePolygon - Setter for the line/polygon drawn by Id Mode, used here to clear it by setting to []
 * @returns {JSX.element} - React component code for the two buttons
 */
export default function MainToolModeButtons( {setBtnGroupState, btntxt1, btntxt2, setEvalModePolygon, setIdModePolygon} ) {
  const [mode, setMode] = React.useState('idmode');
  const handleChange = (event, newMode) => {

    // ensure one button is always active
    if (newMode !== null){
      if (newMode === 'idmode'){
        // clear Eval Mode pipeline from map
        setEvalModePolygon([])
        setBtnGroupState('id')
      } else if (newMode === 'evalmode'){
        // clear Id Mode pipeline from map
        setIdModePolygon([])
        setBtnGroupState('eval')
      }
      setMode(newMode);
    }
  };

  const children = [
    <ToggleButton value="idmode" key="idmode">
      {btntxt1}
    </ToggleButton>,
    <ToggleButton value="evalmode" key="evalmode">
      {btntxt2}
    </ToggleButton>,
  ];

  const control = {
    value: mode,
    onChange: handleChange,
    exclusive: true,
  };

  return (
    <Stack spacing={2} 
      sx={{ 
        alignItems: 'left', 
        padding: '10px',
      }}
    >
      <ToggleButtonGroup color='primary' size="large" {...control} aria-label="Large sizes">
        {children}
      </ToggleButtonGroup>
    </Stack>
  );
}