import * as React from 'react';
import Stack from '@mui/material/Stack';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';

export default function IdModeButtons( {setBtnGroupState, btntxt1, btntxt2, toolMode} ) {
  const [mode, setMode] = React.useState('');


  const handleChange = (event, newMode) => {

    if (newMode === 'rail'){
      setBtnGroupState('rail')
    } else if (newMode === 'route'){
      setBtnGroupState('route')
    }
    setMode(newMode)
  };

  const children = [
    <ToggleButton value="rail" key="rail">
      {btntxt1}
    </ToggleButton>,
    <ToggleButton value="route" key="route">
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
        paddingLeft: '10px',
        paddingBottom: '10px',
      }}
    >
      <ToggleButtonGroup color='secondary' size="small" {...control} aria-label="IdModeButtons" disabled={toolMode !== 'points'}>
        {children}
      </ToggleButtonGroup>
    </Stack>
  );
}