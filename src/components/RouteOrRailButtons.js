import * as React from 'react';
import Stack from '@mui/material/Stack';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';

export default function RouteOrRailButtons( {setBtnGroupState, btntxt1, btntxt2, toolMode} ) {
  const [mode, setMode] = React.useState('route');


  const handleChange = (event, newMode) => {
    // to prevent de-selection, ensures one button is pressed at all times
    if (newMode !== null){
      if (newMode === 'rail'){
        setBtnGroupState('rail')
      } else if (newMode === 'route'){
        setBtnGroupState('route')
      }
      setMode(newMode)
    }
  };

  const children = [
    <ToggleButton value="route" key="route">
      {btntxt1}
    </ToggleButton>,
    <ToggleButton value="rail" key="rail">
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