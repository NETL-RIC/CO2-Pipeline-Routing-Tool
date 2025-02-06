import * as React from 'react';
import Stack from '@mui/material/Stack';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';

export default function MainToolModeButtons( {setBtnGroupState, btntxt1, btntxt2, setShpVals, setLineVals} ) {

  const [mode, setMode] = React.useState('idmode');
  const handleChange = (event, newMode) => {

    // ensure one button is always active
    if (newMode !== null){
      if (newMode === 'idmode'){
        // clear Eval Mode pipeline from map
        setShpVals([])
        setBtnGroupState('points')
      } else if (newMode === 'evalmode'){
        // clear Id Mode pipeline from map
        setLineVals([])
        setBtnGroupState('upld')
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